from django.core.management.base import BaseCommand
from src.importapp.tasks import import_products
from celery.result import AsyncResult


class Command(BaseCommand):
    help = "Запуск импорта данных"

    def handle(self, *args, **options):
        data = options.get('data')
        email = options.get('email')

        result = import_products().delay(data=data, email=email)
        task_id = result.id
        self.stdout.write(self.style.SUCCESS(f"Импорт запущен с ID: {result.id}"))

        task_result = AsyncResult(task_id)
        if task_result.ready():
            if task_result.successful():
                self.stdout.write(self.style.SUCCESS("Импорт завершен успешно."))
            else:
                self.stdout.write(self.style.ERROR("Импорт завершился с ошибкой."))
        else:
            self.stdout.write("Импорт все еще выполняется...")