# Contributing to TCC Therapy Chatbot

Obrigado por considerar contribuir para este projeto! Este é um projeto educacional focado em demonstrar o uso de Small Language Models para aplicações de terapia cognitivo-comportamental.

## 🎯 Como Contribuir

### 1. Fork e Clone

```bash
git clone https://github.com/your-username/tcc-therapy-chatbot.git
cd tcc-therapy-chatbot
```

### 2. Configurar Ambiente

```bash
# Instalar dependências
pip install -r src/requirements.txt

# Copiar configuração
cp config.example.env .env
```

### 3. Fazer Mudanças

- Crie uma branch para sua feature: `git checkout -b feature/nova-funcionalidade`
- Faça suas mudanças
- Teste localmente: `./scripts/test.sh`

### 4. Submeter Pull Request

- Commit suas mudanças: `git commit -m "Add: nova funcionalidade"`
- Push para sua branch: `git push origin feature/nova-funcionalidade`
- Abra um Pull Request no GitHub

## 🚀 Áreas de Contribuição

### Melhorias no Código
- Otimizações de performance
- Melhor tratamento de erros
- Refatoração de código
- Adição de testes

### Novas Funcionalidades
- Novos tipos de análise TCC
- Integração com outros modelos
- Interface web
- Sistema de sessões

### Documentação
- Melhorar README
- Adicionar exemplos
- Documentar APIs
- Guias de deploy

### Análise TCC
- Novos padrões cognitivos
- Técnicas terapêuticas adicionais
- Melhor detecção de emoções
- Sugestões de homework mais específicas

## 📝 Padrões de Código

### Python
- Use type hints
- Siga PEP 8
- Documente funções com docstrings
- Use nomes descritivos

### Commits
- Use mensagens claras
- Formato: `tipo: descrição`
- Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`

### Testes
- Teste suas mudanças
- Adicione testes para novas funcionalidades
- Mantenha cobertura de testes

## 🧪 Testando

```bash
# Teste básico
./scripts/test.sh

# Teste específico
curl -X POST http://localhost:8080/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Seu teste aqui"}'
```

## 🔍 Code Review

### O que procuramos:
- Código limpo e bem documentado
- Testes adequados
- Performance considerada
- Segurança mantida
- Compatibilidade com TCC

### Processo:
1. Review automático (CI/CD)
2. Review manual por mantenedores
3. Discussão se necessário
4. Merge após aprovação

## 🐛 Reportando Bugs

Use o template de issue do GitHub:

```markdown
**Descrição do Bug**
Descrição clara do problema.

**Como Reproduzir**
Passos para reproduzir o comportamento.

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots/Logs**
Se aplicável.

**Ambiente**
- OS: [ex: Ubuntu 20.04]
- Python: [ex: 3.11]
- Versão: [ex: v1.0.0]
```

## 💡 Sugerindo Features

Use o template de feature request:

```markdown
**Feature Request**
Descrição clara da funcionalidade.

**Problema que Resolve**
Qual problema isso resolve?

**Solução Proposta**
Como você imagina que funcionaria?

**Alternativas Consideradas**
Outras soluções que você considerou.

**Contexto Adicional**
Qualquer informação adicional.
```

## 📚 Recursos

- [Documentação TCC](https://exemplo.com)
- [AWS Lambda Docs](https://docs.aws.amazon.com/lambda/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Python Best Practices](https://docs.python.org/3/tutorial/)

## 🤝 Comunidade

- Discord: [Link do servidor]
- Issues: Use o GitHub Issues
- Discussões: GitHub Discussions

## ⚖️ Código de Conduta

Este projeto segue o [Código de Conduta do Contributor Covenant](https://www.contributor-covenant.org/).

### Nossos Compromissos

- Ambiente acolhedor e inclusivo
- Respeito a diferentes pontos de vista
- Aceitação de críticas construtivas
- Foco no que é melhor para a comunidade

### Comportamentos Inaceitáveis

- Linguagem ou imagens sexualizadas
- Trolling, comentários insultuosos
- Assédio público ou privado
- Publicação de informações privadas

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a licença MIT do projeto.

## 🙏 Agradecimentos

Obrigado a todos os contribuidores que tornam este projeto possível!

---

**Lembre-se**: Este é um projeto educacional. Sempre consulte profissionais de saúde mental para questões sérias.
