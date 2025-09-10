# Guia de Uso - TCC Therapy Chatbot

## 🎯 Exemplos de Uso

### 1. Problemas de Ansiedade

**Prompt:**
```json
{
  "prompt": "Estou me sentindo muito ansioso hoje, tenho uma apresentação importante amanhã e não consigo parar de pensar que vou falhar"
}
```

**Resposta Esperada:**
- Identificação de pensamentos catastróficos
- Técnicas de respiração
- Questionamento de evidências
- Estratégias de relaxamento

### 2. Dificuldades no Trabalho

**Prompt:**
```json
{
  "prompt": "Estou passando por um momento difícil no trabalho, me sinto sobrecarregado e não sei como lidar com a pressão"
}
```

**Resposta Esperada:**
- Análise de controle vs. não-controle
- Técnicas de priorização
- Estabelecimento de limites
- Estratégias de gestão de tempo

### 3. Relacionamentos Sociais

**Prompt:**
```json
{
  "prompt": "Tenho problemas para me relacionar com outras pessoas, sempre fico preocupado com o que vão pensar de mim"
}
```

**Resposta Esperada:**
- Questionamento de pensamentos sociais
- Técnicas de comunicação assertiva
- Foco na autenticidade
- Estratégias de exposição gradual

### 4. Depressão e Desânimo

**Prompt:**
```json
{
  "prompt": "Estou me sentindo muito triste e desanimado, não tenho vontade de fazer nada e me sinto sem esperança"
}
```

**Resposta Esperada:**
- Ativação comportamental
- Planejamento de atividades prazerosas
- Técnicas de reestruturação cognitiva
- Foco em pequenos passos

## 🔧 Configurações Avançadas

### Personalizando Respostas

Para adicionar novos tipos de resposta, edite o arquivo `src/tcc_context.py`:

```python
def analyze_client_input(self, prompt: str) -> Dict[str, Any]:
    # Adicione novos padrões aqui
    if "seu_padrão" in prompt.lower():
        analysis["emotional_indicators"].append("nova_emoção")
        analysis["suggested_techniques"].append("nova_técnica")
    
    return analysis
```

### Ajustando Parâmetros

```python
# Em model_manager.py
def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7):
    # Ajuste max_tokens para respostas mais longas/curtas
    # Ajuste temperature para mais/menos criatividade
```

## 📊 Interpretando Respostas

### Estrutura da Resposta

```json
{
  "response": "Texto da resposta TCC",
  "tokens_generated": 182,
  "inference_time": 1.43,
  "model": "tinyllama",
  "timestamp": 1757462750,
  "tcc_analysis": {
    "cognitive_patterns": ["Padrões identificados"],
    "emotional_indicators": ["Emoções detectadas"],
    "behavioral_concerns": ["Comportamentos observados"],
    "suggested_techniques": ["Técnicas recomendadas"],
    "tcc_keywords": ["Palavras-chave TCC"]
  },
  "homework_suggestions": ["Tarefas terapêuticas"]
}
```

### Campos Importantes

- **cognitive_patterns**: Padrões de pensamento identificados
- **emotional_indicators**: Emoções detectadas no texto
- **suggested_techniques**: Técnicas TCC recomendadas
- **homework_suggestions**: Tarefas para o cliente fazer

## 🧪 Testando Diferentes Cenários

### Script de Teste

```bash
#!/bin/bash

# Teste diferentes tipos de problemas
echo "=== Teste Ansiedade ==="
curl -X POST https://your-api.execute-api.region.amazonaws.com/dev/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Estou muito ansioso com a prova de amanhã"}'

echo "=== Teste Trabalho ==="
curl -X POST https://your-api.execute-api.region.amazonaws.com/dev/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Meu chefe está me pressionando muito"}'

echo "=== Teste Relacionamentos ==="
curl -X POST https://your-api.execute-api.region.amazonaws.com/dev/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tenho medo de ser rejeitado pelas pessoas"}'
```

## 🔍 Debugging

### Verificando Status

```bash
curl https://your-api.execute-api.region.amazonaws.com/dev/health
```

### Logs do Lambda

```bash
aws logs tail /aws/lambda/your-function-name --follow
```

### Modo Demo vs. Real

- **Demo Mode**: Respostas simuladas, mais rápidas
- **Real Mode**: Usa Ollama + TinyLlama, respostas mais realistas

## 📈 Otimizações

### Performance

- Use `max_tokens` menor para respostas mais rápidas
- Ajuste `temperature` para consistência vs. criatividade
- Configure timeout adequado no Lambda

### Custo

- Use modo demo para desenvolvimento
- Configure provisioned concurrency para produção
- Monitore uso de memória

## 🚨 Limitações

1. **Não substitui terapia profissional**
2. **Respostas baseadas em padrões pré-definidos**
3. **Não mantém histórico de sessões**
4. **Limitado ao modelo TinyLlama**

## 🔄 Próximos Passos

1. **Adicionar mais modelos**: Integrar outros SLMs
2. **Histórico de sessões**: Persistir conversas
3. **Análise mais sofisticada**: NLP avançado
4. **Interface web**: Frontend para usuários
5. **Integração com terapeutas**: Dashboard profissional
