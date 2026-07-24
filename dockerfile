FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода и картинки
COPY bot.py .
COPY ogo.jpg .

# Запуск бота
CMD ["python", "bot.py"]