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

python src/manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        '${DJANGO_SUPERUSER_EMAIL}',
        '${DJANGO_SUPERUSER_PASSWORD}'
    )
EOF

# Запуск сервера
python src/manage.py runserver 0.0.0.0:8000
