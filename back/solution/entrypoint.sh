#!/bin/sh

# Запускаем Ollama сервер в фоне
echo "Starting Ollama server..."
/bin/ollama serve &

# Ждем запуска сервера
echo "Waiting for Ollama to start..."
sleep 5


# Скачиваем модель
echo "Pulling bambucha/saiga-llama3..."
/bin/ollama run bambucha/saiga-llama3

if [ $? -eq 0 ]; then
    echo "✅ Model bambucha/saiga-llama3 pulled successfully!"
else
    echo "❌ Failed to pull model"
    exit 1
fi

echo "🚀 Ollama is ready with bambucha/saiga-llama3!"

# Бесконечный цикл чтобы контейнер не завершался
tail -f /dev/null