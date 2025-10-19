# Usa uma imagem oficial do Python como base
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências para o container
COPY requirements.txt requirements.txt

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do código do projeto para o diretório de trabalho
COPY . .

# Expõe a porta 5000 para que o Gunicorn possa ser acessado
EXPOSE 5000

# Comando para rodar a aplicação usando Gunicorn (um servidor WSGI de produção)
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
