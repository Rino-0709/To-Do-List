FROM python:3.11-slim

WORKDIR /app

# Копируем requirements и ставим зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# КОПИРУЕМ ВСЁ РЕКУРСИВНО ИЗ ПАПКИ app ПРЯМО В /app
COPY app/. ./

# Теперь внутри контейнера будет:
# /app/main.py
# /app/utils.py  
# /app/static/style.css
# /app/templates/index.html

EXPOSE 80

# Важно: теперь модуль называется просто main, а не app.main
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]