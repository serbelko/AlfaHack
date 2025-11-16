#!/bin/sh

# Запускаем Ollama сервер в фоне
echo "Starting Ollama server..."
/bin/ollama serve &

# Ждем запуска сервера
echo "Waiting for Ollama to start..."
sleep 10


# Скачиваем модель
echo "Pulling bambucha/saiga-llama3..."
/bin/ollama run bambucha/saiga-llama3