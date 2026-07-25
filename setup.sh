#!/usr/bin/env bash

echo "Subindo o ambiente..."

echo "Parando os containers antigos..."
docker-compose down

echo "Construindo a imagem do projeto..."
docker-compose build

echo "Iniciando os containers..."
echo "Pressione Ctrl+C para encerrar."

docker-compose up