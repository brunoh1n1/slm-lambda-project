# Dockerfile for SLM Lambda Project
# Baseado na proposta do AWS Builder

FROM public.ecr.aws/lambda/python:3.11

# Instalar dependências do sistema
RUN yum update -y && \
    yum install -y \
    curl \
    tar \
    gzip \
    && yum clean all

# Instalar Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copiar código da aplicação
COPY src/ ${LAMBDA_TASK_ROOT}/

# Instalar dependências Python
RUN pip install -r requirements.txt

# Configurar variáveis de ambiente
ENV MODEL_NAME=llama2:7b
ENV MAX_TOKENS=512
ENV TEMPERATURE=0.7
ENV CACHE_TTL=3600
ENV ENABLE_STREAMING=false
ENV OLLAMA_HOST=http://localhost:11434

# Expor porta
EXPOSE 8080

# Comando de inicialização
CMD ["lambda_function.lambda_handler"]
