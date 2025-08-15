FROM python:3.9

# Устанавливаем рабочую директорию — это будет корень проекта
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВЕСЬ код из backend/foodgram/ в /app
COPY foodgram/ /app/


# Запускаем Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi:application"]
