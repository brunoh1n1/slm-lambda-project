# TCC Therapy Chatbot - AWS Lambda

Um chatbot especializado em Terapia Cognitivo-Comportamental (TCC) executando em AWS Lambda com Small Language Models (SLMs).

## 🎯 Características

- **Especializado em TCC**: Respostas baseadas em técnicas de Terapia Cognitivo-Comportamental
- **Respostas Contextuais**: Diferentes respostas baseadas no tipo de problema (ansiedade, depressão, trabalho, relacionamentos)
- **Modo Demo**: Funciona sem Ollama para demonstrações
- **Análise TCC**: Identifica padrões cognitivos e sugere técnicas terapêuticas
- **Sugestões de Tarefas**: Oferece "homework" terapêutico personalizado

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│   AWS Lambda     │───▶│   Ollama (CPU)  │
│                 │    │   (Python 3.11)  │    │   + TinyLlama   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Estrutura do Projeto

```
slm-lambda-project/
├── src/                          # Código fonte
│   ├── lambda_function.py        # Handler principal do Lambda
│   ├── model_manager.py          # Gerenciamento do modelo e Ollama
│   ├── tcc_context.py            # Contexto e análise TCC
│   ├── utils.py                  # Utilitários e validação
│   └── requirements.txt          # Dependências Python
├── infrastructure/               # Infraestrutura Terraform
│   ├── lambda.tf                 # Recursos Lambda
│   ├── api-gateway.tf            # API Gateway
│   ├── variables.tf              # Variáveis Terraform
│   ├── outputs.tf                # Outputs Terraform
│   ├── providers.tf              # Providers Terraform
│   └── terraform.tfvars.example  # Exemplo de variáveis
├── scripts/                      # Scripts de deploy e teste
│   ├── deploy.sh                 # Script de deploy automático
│   └── test.sh                   # Script de teste
├── Dockerfile                    # Container para desenvolvimento
├── Dockerfile.lambda             # Container otimizado para Lambda
├── ollama-config.yaml            # Configuração do Ollama
├── config.example.env            # Exemplo de variáveis de ambiente
├── README.md                     # Documentação principal
├── USAGE.md                      # Guia de uso detalhado
├── CONTRIBUTING.md               # Guia de contribuição
├── LICENSE                       # Licença MIT
└── .gitignore                    # Arquivos ignorados
```

## 🚀 Como Usar

### 1. Deploy Local (Desenvolvimento)

```bash
# Clone o repositório
git clone <repository-url>
cd slm-lambda-project

# Instale dependências
pip install -r src/requirements.txt

# Execute localmente
python src/lambda_function.py
```

### 2. Deploy AWS Lambda (Recomendado)

#### Deploy Automático com Script

```bash
# Configure suas credenciais AWS
aws configure

# Execute o script de deploy
./scripts/deploy.sh

# Ou com parâmetros customizados
./scripts/deploy.sh --region us-east-1 --function-name meu-chatbot
```

#### Deploy Manual com Terraform

```bash
# Configure as variáveis
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars com seus valores

# Deploy da infraestrutura
terraform init
terraform plan
terraform apply

# Build e push da imagem Docker
docker build -f Dockerfile.lambda -t tcc-chatbot .
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-2.amazonaws.com
docker tag tcc-chatbot:latest <account>.dkr.ecr.us-east-2.amazonaws.com/tcc-chatbot:latest
docker push <account>.dkr.ecr.us-east-2.amazonaws.com/tcc-chatbot:latest

# Atualizar Lambda
aws lambda update-function-code \
  --function-name tcc-chatbot \
  --image-uri <account>.dkr.ecr.us-east-2.amazonaws.com/tcc-chatbot:latest
```

### 3. Deploy Manual (Sem Terraform)

#### Opção A: Container Image

```bash
# Build da imagem
docker build -f Dockerfile.lambda -t tcc-chatbot .

# Tag para ECR
docker tag tcc-chatbot:latest <account>.dkr.ecr.<region>.amazonaws.com/tcc-chatbot:latest

# Push para ECR
docker push <account>.dkr.ecr.<region>.amazonaws.com/tcc-chatbot:latest

# Deploy no Lambda
aws lambda create-function \
  --function-name tcc-chatbot \
  --package-type Image \
  --code ImageUri=<account>.dkr.ecr.<region>.amazonaws.com/tcc-chatbot:latest \
  --role arn:aws:iam::<account>:role/lambda-execution-role \
  --timeout 300 \
  --memory-size 3008
```

#### Opção B: ZIP Package

```bash
# Crie um ZIP com o código
cd src
zip -r ../tcc-chatbot.zip .

# Deploy no Lambda
aws lambda create-function \
  --function-name tcc-chatbot \
  --runtime python3.11 \
  --role arn:aws:iam::<account>:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://tcc-chatbot.zip \
  --timeout 300 \
  --memory-size 3008
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
MODEL_NAME=tinyllama              # Nome do modelo Ollama
OLLAMA_HOST=0.0.0.0:11434        # Host do Ollama
TEMPERATURE=0.7                   # Temperatura para geração
MAX_TOKENS=512                    # Máximo de tokens
TCC_MODE=true                     # Ativar modo TCC
OLLAMA_CPU_ONLY=1                 # Usar apenas CPU
```

### Configuração do Ollama

O arquivo `ollama-config.yaml` contém configurações para o Ollama:

```yaml
model: tinyllama
temperature: 0.7
max_tokens: 512
cpu_only: true
```

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "model": "tinyllama",
  "model_status": {
    "loaded": true,
    "demo_mode": false,
    "tcc_enabled": true
  },
  "timestamp": 1757462764
}
```

### Inference
```bash
POST /inference
Content-Type: application/json

{
  "prompt": "Estou me sentindo muito ansioso hoje",
  "max_tokens": 512,
  "temperature": 0.7
}
```

**Resposta:**
```json
{
  "response": "Entendo que você está se sentindo ansioso(a)...",
  "tokens_generated": 182,
  "inference_time": 1.43,
  "model": "tinyllama",
  "timestamp": 1757462750,
  "tcc_analysis": {
    "cognitive_patterns": ["Pensamento absolutista: 'não consigo'"],
    "emotional_indicators": ["ansiedade"],
    "suggested_techniques": ["Reestruturação cognitiva", "Técnicas de relaxamento"]
  },
  "homework_suggestions": [
    "Registre seus pensamentos automáticos em um diário por uma semana"
  ]
}
```

## 🧠 Tipos de Resposta TCC

O sistema identifica automaticamente o contexto e fornece respostas especializadas:

### Ansiedade
- Técnicas de respiração
- Questionamento de pensamentos
- Exposição gradual

### Depressão
- Ativação comportamental
- Planejamento de atividades
- Técnicas de reestruturação cognitiva

### Trabalho
- Gestão de estresse
- Estabelecimento de limites
- Técnicas de priorização

### Relacionamentos
- Comunicação assertiva
- Questionamento de pensamentos sociais
- Foco na autenticidade

### Casos Gerais
- Respostas variadas baseadas em TCC
- Técnicas de questionamento cognitivo
- Foco em soluções práticas

## 🧪 Testando

```bash
# Teste local
curl -X POST http://localhost:8080/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Estou passando por um momento difícil no trabalho"}'

# Teste AWS
curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tenho problemas para me relacionar com outras pessoas"}'
```

## 🔍 Modo Demo

Quando o Ollama não está disponível, o sistema automaticamente entra em modo demo, fornecendo respostas TCC simuladas mas realistas.

## 📊 Monitoramento

- **CloudWatch Logs**: Logs detalhados de execução
- **Métricas**: Tempo de inferência, tokens gerados, uso de memória
- **Health Check**: Endpoint para verificar status do sistema

## 🛠️ Desenvolvimento

### Estrutura do Código

- `lambda_function.py`: Handler principal, roteamento de requests
- `model_manager.py`: Gerenciamento do modelo, integração com Ollama
- `tcc_context.py`: Análise TCC, geração de respostas especializadas
- `utils.py`: Validação, formatação de respostas

### Adicionando Novos Tipos de Resposta

1. Edite `tcc_context.py` para adicionar novos padrões
2. Modifique `model_manager.py` para incluir novas condições
3. Teste com diferentes prompts

## 📝 Licença

Este projeto é fornecido como exemplo educacional. Use com responsabilidade e sempre consulte profissionais de saúde mental para questões sérias.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## ⚠️ Disclaimer

Este chatbot é apenas para fins educacionais e de demonstração. Não substitui terapia profissional. Sempre consulte um terapeuta qualificado para questões de saúde mental.