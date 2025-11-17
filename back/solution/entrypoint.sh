#!/bin/sh

# Запускаем Ollama сервер в фоне
echo "Starting Ollama server..."
/bin/ollama serve &
OLLAMA_PID=$!

# Ждем запуска сервера
echo "Waiting for Ollama to start..."
sleep 10

# Скачиваем модель (если ещё не скачана)
echo "Pulling bambucha/saiga-llama3..."
/bin/ollama pull bambucha/saiga-llama3

echo "Ollama is ready"

# Поддерживаем контейнер живым, пока работает ollama serve
wait $OLLAMA_PID