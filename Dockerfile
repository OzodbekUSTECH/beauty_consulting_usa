FROM python:3.12-slim

# Установить нужные пакеты
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Настройки Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Рабочая директория
WORKDIR /code

# Копирование зависимостей и установка
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Копирование кода проекта
COPY . .

# Создание пользователя
RUN useradd -u 1000 -m user \
 && chown -R user:user /code

# Переход под пользователя
USER user

# Убедиться, что скрипт имеет права на исполнение
RUN chmod +x /code/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
