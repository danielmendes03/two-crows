#!/bin/bash

# Script para iniciar a aplicação Two Crows com Docker Compose

echo "Iniciando a aplicação Two Crows com Docker Compose..."

# ATUALIZADO: Usando 'docker-compose' (v1, com hífen) para compatibilidade
docker-compose up -d --build

# Espera um pouco para o container web estar pronto
sleep 5

# Verifica se a base de dados já existe dentro do volume
if docker-compose exec web [ ! -f "instance/database.db" ]; then
    echo "Base de dados não encontrada. Inicializando..."
    docker-compose exec web flask init-db
else
    echo "Base de dados já existente."
fi

echo ""
# Captura o IP local da máquina para exibição
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "Aplicação está rodando em http://$LOCAL_IP (ou http://localhost)"
echo "Para parar os containers, rode: docker-compose down"
echo ""