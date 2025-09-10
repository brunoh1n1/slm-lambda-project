"""
Sistema de Contexto para Terapia Cognitivo-Comportamental (TCC)
"""

import json
from typing import Dict, List, Any
import structlog

logger = structlog.get_logger()

class TCCContextManager:
    """Gerenciador de contexto para Terapia Cognitivo-Comportamental"""
    
    def __init__(self):
        self.tcc_principles = {
            "cognitive_restructuring": [
                "Identificação de pensamentos automáticos negativos",
                "Questionamento de evidências para pensamentos",
                "Desenvolvimento de pensamentos alternativos mais realistas",
                "Técnicas de reestruturação cognitiva"
            ],
            "behavioral_techniques": [
                "Ativação comportamental",
                "Exposição gradual",
                "Técnicas de relaxamento",
                "Planejamento de atividades prazerosas"
            ],
            "mindfulness": [
                "Atenção plena ao momento presente",
                "Observação sem julgamento",
                "Técnicas de respiração consciente",
                "Meditação mindfulness"
            ],
            "problem_solving": [
                "Definição clara do problema",
                "Geração de soluções alternativas",
                "Avaliação de prós e contras",
                "Implementação e monitoramento"
            ]
        }
        
        self.tcc_phrases = {
            "empathy": [
                "Entendo como você se sente",
                "É compreensível que você tenha essa reação",
                "Seus sentimentos são válidos",
                "Posso imaginar como isso deve ser difícil para você"
            ],
            "collaboration": [
                "Vamos trabalhar juntos nisso",
                "Que tal explorarmos essa situação juntos?",
                "O que você acha que poderia ajudar?",
                "Vamos descobrir estratégias que funcionem para você"
            ],
            "psychoeducation": [
                "Na TCC, aprendemos que nossos pensamentos influenciam nossos sentimentos",
                "É importante distinguir entre fatos e interpretações",
                "Nossos pensamentos automáticos nem sempre refletem a realidade",
                "Podemos aprender a questionar nossos pensamentos negativos"
            ],
            "intervention": [
                "Que evidências você tem para esse pensamento?",
                "Existe uma forma alternativa de ver essa situação?",
                "O que você diria a um amigo na mesma situação?",
                "Que estratégias você já usou que funcionaram antes?"
            ]
        }
        
        self.session_context = {
            "current_technique": None,
            "client_concerns": [],
            "goals": [],
            "homework": [],
            "progress_notes": []
        }
    
    def get_tcc_system_prompt(self) -> str:
        """Retorna o prompt do sistema com contexto TCC"""
        return """Você é um assistente especializado em Terapia Cognitivo-Comportamental (TCC). 

PRINCÍPIOS FUNDAMENTAIS DA TCC:
- Conexão entre pensamentos, sentimentos e comportamentos
- Foco no presente e em soluções práticas
- Colaboração ativa com o cliente
- Uso de técnicas baseadas em evidências
- Objetivos específicos e mensuráveis

TÉCNICAS PRINCIPAIS:
1. Reestruturação Cognitiva: Identificar e questionar pensamentos automáticos negativos
2. Ativação Comportamental: Aumentar atividades prazerosas e funcionais
3. Exposição: Enfrentar gradualmente situações temidas
4. Resolução de Problemas: Estratégias sistemáticas para lidar com desafios
5. Mindfulness: Atenção plena e aceitação

ESTILO DE COMUNICAÇÃO:
- Empático e acolhedor
- Colaborativo e não-diretivo
- Focado em soluções
- Linguagem clara e acessível
- Perguntas abertas que promovem reflexão

SEMPRE:
- Valide os sentimentos do cliente
- Use técnicas baseadas em evidências
- Mantenha foco no presente
- Promova autonomia e autoeficácia
- Sugira exercícios práticos quando apropriado

NUNCA:
- Dê conselhos médicos ou diagnósticos
- Substitua terapia profissional
- Minimize a dor emocional
- Use linguagem técnica excessiva
- Seja diretivo demais"""
    
    def analyze_client_input(self, input_text: str) -> Dict[str, Any]:
        """Analisa a entrada do cliente e identifica áreas de intervenção TCC"""
        analysis = {
            "cognitive_patterns": [],
            "emotional_indicators": [],
            "behavioral_concerns": [],
            "suggested_techniques": [],
            "tcc_keywords": []
        }
        
        # Identificar padrões cognitivos
        cognitive_keywords = [
            "sempre", "nunca", "todos", "ninguém", "deveria", "tenho que",
            "não consigo", "impossível", "terrível", "catastrófico"
        ]
        
        for keyword in cognitive_keywords:
            if keyword.lower() in input_text.lower():
                analysis["cognitive_patterns"].append(f"Pensamento absolutista: '{keyword}'")
                analysis["suggested_techniques"].append("Reestruturação cognitiva")
        
        # Identificar indicadores emocionais
        emotional_keywords = {
            "ansiedade": ["ansioso", "preocupado", "nervoso", "tenso", "medo"],
            "depressão": ["triste", "desanimado", "sem esperança", "vazio", "culpa"],
            "raiva": ["irritado", "furioso", "revoltado", "frustrado"],
            "estresse": ["estressado", "sobrecarregado", "pressão", "correria"]
        }
        
        for emotion, keywords in emotional_keywords.items():
            for keyword in keywords:
                if keyword.lower() in input_text.lower():
                    analysis["emotional_indicators"].append(emotion)
                    analysis["tcc_keywords"].append(keyword)
        
        # Sugerir técnicas baseadas na análise
        if "ansiedade" in analysis["emotional_indicators"]:
            analysis["suggested_techniques"].extend([
                "Técnicas de relaxamento",
                "Exposição gradual",
                "Mindfulness"
            ])
        
        if "depressão" in analysis["emotional_indicators"]:
            analysis["suggested_techniques"].extend([
                "Ativação comportamental",
                "Reestruturação cognitiva",
                "Planejamento de atividades"
            ])
        
        return analysis
    
    def generate_tcc_response(self, client_input: str, analysis: Dict[str, Any]) -> str:
        """Gera uma resposta baseada em princípios TCC"""
        # Adicionar contexto da sessão
        context = f"""
CONTEXTO DA SESSÃO:
- Técnicas sugeridas: {', '.join(analysis['suggested_techniques'])}
- Padrões cognitivos identificados: {', '.join(analysis['cognitive_patterns'])}
- Indicadores emocionais: {', '.join(analysis['emotional_indicators'])}

ENTRADA DO CLIENTE: {client_input}

INSTRUÇÕES:
1. Responda de forma empática e acolhedora
2. Use técnicas TCC apropriadas
3. Faça perguntas que promovam reflexão
4. Sugira exercícios práticos quando relevante
5. Mantenha foco em soluções e no presente
6. Promova autonomia do cliente
"""
        return context
    
    def get_homework_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Sugere exercícios para casa baseados na análise"""
        homework = []
        
        if "Reestruturação cognitiva" in analysis["suggested_techniques"]:
            homework.append(
                "Registre seus pensamentos automáticos em um diário por uma semana. "
                "Para cada pensamento negativo, pergunte-se: 'Que evidências tenho para isso?'"
            )
        
        if "Ativação comportamental" in analysis["suggested_techniques"]:
            homework.append(
                "Planeje uma atividade prazerosa para cada dia da próxima semana. "
                "Registre como se sentiu antes e depois de cada atividade."
            )
        
        if "Mindfulness" in analysis["suggested_techniques"]:
            homework.append(
                "Pratique 5 minutos de respiração consciente por dia. "
                "Foque na respiração e observe seus pensamentos sem julgamento."
            )
        
        if "Exposição gradual" in analysis["suggested_techniques"]:
            homework.append(
                "Crie uma lista de situações que você evita, ordenadas por nível de ansiedade. "
                "Comece enfrentando a situação menos ansiosa."
            )
        
        return homework
    
    def update_session_context(self, client_input: str, analysis: Dict[str, Any], response: str):
        """Atualiza o contexto da sessão"""
        self.session_context["client_concerns"].append({
            "input": client_input,
            "analysis": analysis,
            "timestamp": "current_session"
        })
        
        if analysis["suggested_techniques"]:
            self.session_context["current_technique"] = analysis["suggested_techniques"][0]
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Retorna um resumo da sessão"""
        return {
            "techniques_used": list(set([
                technique for concern in self.session_context["client_concerns"]
                for technique in concern["analysis"]["suggested_techniques"]
            ])),
            "main_concerns": [concern["input"] for concern in self.session_context["client_concerns"]],
            "homework_suggestions": self.get_homework_suggestions({
                "suggested_techniques": list(set([
                    technique for concern in self.session_context["client_concerns"]
                    for technique in concern["analysis"]["suggested_techniques"]
                ]))
            }),
            "progress_notes": self.session_context["progress_notes"]
        }
