# Imagem base oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os requisitos para o container
COPY api/requirements.txt /app

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o Uvicorn vai usar
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]