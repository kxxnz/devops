#!/usr/bin/env bash

echo "Subindo o ambiente..."

echo "Parando os containers antigos..."
docker-compose down

echo "Construindo a imagem do projeto..."
docker-compose build

echo "Subindo os containers..."
docker-compose up

echo "Ambiente subido com sucesso!"