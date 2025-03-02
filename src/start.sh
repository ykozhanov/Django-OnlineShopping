#!/bin/bash

# Функция для проверки доступности базы данных
wait_for_db() {
    while ! nc -z ${DB_HOST} ${DB_PORT}; do
        echo "Ожидание запуска базы данных..."
        sleep 1
    done
    echo "База данных доступна!"
}

# Ожидание базы данных
wait_for_db

# Выполнение миграций
python src/manage.py migrate

python src/manage.py createsuperuser

# Запуск сервера
python src/manage.py runserver 0.0.0.0:8000
