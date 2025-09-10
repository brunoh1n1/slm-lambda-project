import os
import json
import time
import logging
import subprocess
import boto3
from typing import Dict, Any, Optional
from utils import sanitize_prompt, calculate_tokens
from tcc_context import TCCContextManager

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages Small Language Model loading, caching, and inference using Ollama
    """
    
    def __init__(self, model_name: str, s3_bucket: str = '', cache_ttl: int = 3600):
        self.model_name = model_name
        self.s3_bucket = s3_bucket
        self.cache_ttl = cache_ttl
        self.model_loaded = False
        self.last_activity = 0
        self.demo_mode = False
        self.s3_client = boto3.client('s3') if s3_bucket else None
        
        # Initialize TCC Context Manager
        self.tcc_context = TCCContextManager()
        
        # Initialize Ollama
        self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize Ollama service"""
        try:
            # Try to start Ollama using the initialization script
            try:
                logger.info("Attempting to start Ollama using initialization script...")
                result = subprocess.run(['bash', '/var/task/start-ollama.sh'],
                                      capture_output=True, text=True, timeout=60)
                logger.info(f"Ollama start script output: {result.stdout}")
                if result.stderr:
                    logger.warning(f"Ollama start script errors: {result.stderr}")
            except Exception as e:
                logger.warning(f"Failed to run Ollama start script: {str(e)}")

            # Check multiple possible paths for ollama
            ollama_paths = ['/usr/local/bin/ollama', 'ollama', '/opt/python/ollama', '/var/task/ollama']
            ollama_found = False
            ollama_path = None

            for path in ollama_paths:
                try:
                    result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        logger.info(f"Ollama found at: {path}")
                        ollama_found = True
                        ollama_path = path
                        break
                except:
                    continue

            if not ollama_found:
                logger.warning("Ollama not found in any expected location")
                self.demo_mode = True
                return

            # Check if Ollama is running
            result = subprocess.run([ollama_path, 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.info("Ollama found but not running - attempting to start...")
                self._start_ollama(ollama_path)
            else:
                logger.info("Ollama found and running")
                self.demo_mode = False
                
            # Update demo_mode based on Ollama availability
            if ollama_found:
                self.demo_mode = False
        except FileNotFoundError:
            logger.warning("Ollama not found - running in demo mode")
            self.demo_mode = True
        except Exception as e:
            logger.warning(f"Ollama not available - running in demo mode: {str(e)}")
            self.demo_mode = True
    
    def _start_ollama(self, ollama_path=None):
        """Start Ollama service"""
        try:
            if ollama_path is None:
                ollama_path = 'ollama'
            
            # Try to start Ollama using the layer script if available
            start_script = "/opt/python/start_ollama.sh"
            if os.path.exists(start_script):
                logger.info("Starting Ollama using layer script...")
                result = subprocess.run(['bash', start_script], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info("Ollama started successfully via layer script")
                    self.demo_mode = False
                    return
                else:
                    logger.warning(f"Layer script failed: {result.stderr}")
            
            # Fallback: try to start Ollama directly
            logger.info(f"Starting Ollama directly using {ollama_path}...")
            process = subprocess.Popen([ollama_path, 'serve'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            
            # Wait a bit for Ollama to start
            time.sleep(5)
            
            # Check if it's running
            result = subprocess.run([ollama_path, 'list'], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                logger.info("Ollama started successfully")
                self.demo_mode = False
            else:
                logger.warning("Failed to start Ollama - running in demo mode")
                self.demo_mode = True
        except Exception as e:
            logger.warning(f"Failed to start Ollama - running in demo mode: {str(e)}")
            self.demo_mode = True
    
    def _ensure_model_loaded(self):
        """Ensure the model is loaded and ready"""
        if not self.model_loaded:
            self._load_model()
    
    def _load_model(self):
        """Load the specified model"""
        try:
            # Check if Ollama is available
            ollama_available = False
            try:
                result = subprocess.run(['ollama', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    ollama_available = True
                    logger.info("Ollama is available for real model loading")
            except:
                pass
            
            if not ollama_available or self.demo_mode:
                logger.info(f"Demo mode: Simulating model {self.model_name} loading...")
                self.model_loaded = True
                self.last_activity = time.time()
                logger.info(f"Demo model {self.model_name} loaded successfully")
                return
                
            logger.info(f"Loading model: {self.model_name}")
            
            # Check if model exists locally
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            
            if self.model_name not in result.stdout:
                logger.info(f"Model {self.model_name} not found, pulling...")
                self._pull_model()
            
            # Load model
            result = subprocess.run(['ollama', 'run', self.model_name, '--version'],
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.model_loaded = True
                self.last_activity = time.time()
                logger.info(f"Model {self.model_name} loaded successfully")
            else:
                raise Exception(f"Failed to load model: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def _pull_model(self):
        """Pull model from Ollama registry"""
        try:
            logger.info(f"Pulling model {self.model_name}...")
            result = subprocess.run(['ollama', 'pull', self.model_name],
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise Exception(f"Failed to pull model: {result.stderr}")
                
            logger.info(f"Model {self.model_name} pulled successfully")
            
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            raise
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text using the loaded model with TCC context
        """
        try:
            self._ensure_model_loaded()
            
            # Sanitize prompt
            clean_prompt = sanitize_prompt(prompt)
            
            if self.demo_mode:
                return self._demo_generate(clean_prompt, max_tokens, temperature)
            
            # Analyze client input for TCC context
            analysis = self.tcc_context.analyze_client_input(clean_prompt)
            
            # Generate TCC-enhanced prompt
            tcc_prompt = self.tcc_context.generate_tcc_response(clean_prompt, analysis)
            
            # Prepare Ollama command with TCC system prompt
            system_prompt = self.tcc_context.get_tcc_system_prompt()
            
            cmd = [
                'ollama', 'generate', self.model_name,
                '--system', system_prompt,
                '--prompt', tcc_prompt,
                '--options', json.dumps({
                    'num_predict': max_tokens,
                    'temperature': temperature,
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                })
            ]
            
            # Execute generation
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            generation_time = time.time() - start_time
            
            if result.returncode != 0:
                raise Exception(f"Generation failed: {result.stderr}")
            
            # Parse response
            response_text = result.stdout.strip()
            tokens_generated = calculate_tokens(response_text)
            
            # Update session context
            self.tcc_context.update_session_context(clean_prompt, analysis, response_text)
            
            self.last_activity = time.time()
            
            return {
                'text': response_text,
                'tokens_generated': tokens_generated,
                'generation_time': round(generation_time, 2),
                'model': self.model_name,
                'tcc_analysis': analysis,
                'homework_suggestions': self.tcc_context.get_homework_suggestions(analysis)
            }
            
        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            raise
    
    def _demo_generate(self, prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Demo mode text generation with TCC context"""
        import random
        
        # Simulate generation time
        generation_time = random.uniform(0.5, 2.0)
        time.sleep(generation_time)
        
        # Analyze client input for TCC context
        analysis = self.tcc_context.analyze_client_input(prompt)
        
        # Generate TCC-specific demo responses
        if "ansiedade" in analysis["emotional_indicators"]:
            response_text = """Entendo que você está se sentindo ansioso(a) com a apresentação de amanhã. É natural sentir essa preocupação, mas vamos trabalhar juntos para gerenciar esses sentimentos.

Na Terapia Cognitivo-Comportamental, aprendemos que nossos pensamentos influenciam diretamente nossos sentimentos. Quando pensamos "vou falhar", isso gera ansiedade.

Vamos questionar esse pensamento: que evidências você tem de que vai falhar? Já fez apresentações antes? O que aconteceu? 

Que tal praticarmos algumas técnicas de relaxamento? Respire fundo por 4 segundos, segure por 4 segundos, e expire por 6 segundos. Repita isso algumas vezes.

Lembre-se: você está preparado(a) e tem capacidade para isso. Vamos focar no que você pode controlar agora."""
            
        elif "depressão" in analysis["emotional_indicators"]:
            response_text = """Vejo que você está passando por um momento difícil. Seus sentimentos são válidos e é importante reconhecê-los.

Na TCC, trabalhamos com a ideia de que podemos aprender a identificar padrões de pensamento que contribuem para esses sentimentos. 

Que tal começarmos com uma pequena atividade? Mesmo que não tenha vontade, tente fazer algo pequeno e prazeroso hoje - pode ser ouvir uma música que gosta, dar uma caminhada curta, ou ligar para alguém especial.

Lembre-se: você não está sozinho(a) nisso. Pequenos passos podem fazer uma grande diferença."""
            
        elif "trabalho" in prompt.lower() or "trabalho" in analysis["tcc_keywords"]:
            response_text = """Entendo que você está passando por dificuldades no trabalho. Isso pode ser muito desafiador e é importante reconhecer o impacto que isso tem em você.

Na TCC, trabalhamos com a ideia de que podemos identificar padrões de pensamento que podem estar contribuindo para o estresse no trabalho.

Vamos explorar isso juntos: que situações específicas no trabalho estão te causando mais preocupação? Como você tem lidado com essas situações até agora?

Que tal pensarmos em algumas estratégias práticas? Por exemplo, você poderia:
- Identificar quais aspectos do trabalho você pode controlar
- Praticar técnicas de respiração antes de reuniões importantes
- Estabelecer limites claros entre trabalho e vida pessoal

O que você acha que seria mais útil para começar?"""
            
        elif "relacionamento" in prompt.lower() or "pessoas" in prompt.lower():
            response_text = """Vejo que você está enfrentando desafios nos relacionamentos. Isso pode ser muito doloroso e é compreensível que você esteja se sentindo assim.

Na TCC, aprendemos que nossos pensamentos sobre as situações sociais podem influenciar como nos sentimos e nos comportamos.

Vamos refletir juntos: que pensamentos você tem quando está em situações sociais? Você se preocupa com o que os outros pensam de você?

Algumas estratégias que podem ajudar:
- Praticar a comunicação assertiva
- Questionar pensamentos como "todos vão me julgar"
- Focar em ser autêntico(a) em vez de tentar agradar todos

Que tipo de situação social te causa mais ansiedade?"""
            
        elif "sobrecarregado" in prompt.lower() or "responsabilidades" in prompt.lower():
            response_text = """Entendo que você está se sentindo sobrecarregado(a) com tantas responsabilidades. É natural se sentir assim quando temos muitas coisas para cuidar.

Na TCC, trabalhamos com técnicas de resolução de problemas e priorização para lidar com situações como essa.

Vamos começar organizando isso: que responsabilidades você considera mais urgentes? E quais são mais importantes para você?

Algumas estratégias que podem ajudar:
- Fazer uma lista de todas as responsabilidades
- Priorizar por urgência e importância
- Quebrar tarefas grandes em passos menores
- Praticar dizer "não" quando necessário

Que responsabilidade está te causando mais estresse no momento?"""
            
        else:
            # Respostas mais variadas para casos gerais
            import random
            general_responses = [
                """Obrigado por compartilhar isso comigo. Na Terapia Cognitivo-Comportamental, valorizamos muito a colaboração e o trabalho conjunto.

Vamos explorar sua situação juntos. O que você acha que poderia ajudar neste momento? Que estratégias você já usou antes que funcionaram?

Na TCC, focamos no presente e em soluções práticas. Que pequeno passo você poderia dar hoje para se sentir melhor?""",
                
                """Entendo que você está passando por um momento desafiador. É importante reconhecer que buscar ajuda é um sinal de força, não de fraqueza.

Na TCC, trabalhamos com a ideia de que podemos aprender a identificar e modificar padrões de pensamento que não estão nos servindo bem.

Vamos começar explorando: como você tem interpretado essa situação? Que pensamentos passam pela sua cabeça quando pensa nisso?

Que tal tentarmos uma técnica simples? Quando notar um pensamento negativo, pergunte-se: 'Isso é um fato ou uma interpretação?'""",
                
                """Vejo que você está enfrentando uma situação difícil. Seus sentimentos são válidos e é importante dar espaço para eles.

Na TCC, aprendemos que nossos pensamentos, sentimentos e comportamentos estão todos conectados. Quando mudamos um, podemos influenciar os outros.

Vamos trabalhar juntos: que emoções você está sentindo com mais intensidade? E que comportamentos você tem notado em si mesmo(a)?

Uma técnica que pode ajudar é o "check-in emocional": reserve alguns minutos por dia para identificar e nomear suas emoções sem julgamento."""
            ]
            response_text = random.choice(general_responses)
        
        tokens_generated = calculate_tokens(response_text)
        
        # Update session context
        self.tcc_context.update_session_context(prompt, analysis, response_text)
        
        self.last_activity = time.time()
        
        return {
            'text': response_text,
            'tokens_generated': tokens_generated,
            'generation_time': round(generation_time, 2),
            'model': f"{self.model_name} (TCC demo mode)",
            'tcc_analysis': analysis,
            'homework_suggestions': self.tcc_context.get_homework_suggestions(analysis)
        }
    
    def warmup(self):
        """Warm up the model with a simple request"""
        try:
            logger.info("Warming up model...")
            if self.demo_mode:
                logger.info("Demo mode: Simulating model warmup...")
                time.sleep(0.5)  # Simulate warmup time
                logger.info("Demo model warmup completed")
            else:
                self.generate("Hello", max_tokens=10, temperature=0.1)
                logger.info("Model warmup completed")
        except Exception as e:
            logger.error(f"Warmup error: {str(e)}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get model status with TCC context"""
        status = {
            'loaded': self.model_loaded,
            'model_name': self.model_name,
            'last_activity': self.last_activity,
            'cache_ttl': self.cache_ttl,
            'demo_mode': self.demo_mode,
            'tcc_enabled': True,
            'session_summary': self.tcc_context.get_session_summary()
        }
        return status
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.model_loaded:
                # Unload model to free memory
                subprocess.run(['ollama', 'stop', self.model_name], 
                             capture_output=True, timeout=30)
                self.model_loaded = False
                logger.info("Model unloaded")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
    
    def _cache_to_s3(self, data: Dict[str, Any], key: str):
        """Cache data to S3"""
        if not self.s3_client or not self.s3_bucket:
            return
        
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
        except Exception as e:
            logger.error(f"S3 cache error: {str(e)}")
    
    def _get_from_s3_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from S3 cache"""
        if not self.s3_client or not self.s3_bucket:
            return None
        
        try:
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=key)
            return json.loads(response['Body'].read())
        except Exception as e:
            logger.debug(f"S3 cache miss: {str(e)}")
            return None