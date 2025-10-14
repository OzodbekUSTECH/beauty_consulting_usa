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
COPY . /code/

# Установка прав на скрипт запуска
RUN chmod +x ./entrypoint.sh

# Создание пользователя и переход на него
RUN useradd -m user
RUN chown -R user:user /code
USER user

# Запуск приложения
ENTRYPOINT ["./entrypoint.sh"]