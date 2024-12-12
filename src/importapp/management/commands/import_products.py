import json
import shutil
from pathlib import Path

from celery.result import AsyncResult
from django.core.management.base import BaseCommand
from django.conf import settings

from src.importapp.tasks import import_products


class Command(BaseCommand):
    help = "Запуск импорта данных"

    def add_arguments(self, parser):
        parser.add_argument("path_file", type=str, help="Путь к JSON файлу для импорта.")
        parser.add_argument("email", type=str, help="Email для уведомлений.")

    def handle(self, *args, **options):
        email = options.get("email")
        path_file = Path(options.get("path_file"))
        success_dir: Path = settings.MEDIA_ROOT / "processed_success"
        failed_dir: Path = settings.MEDIA_ROOT / "processed_failed"

        if not path_file.exists():
            self.stdout.write(self.style.ERROR(f"Файл {path_file} не найден."))
            return

        try:
            with open(path_file, "r") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR("Ошибка при чтении JSON файла."))

        result = import_products().delay(data=data, email=email)
        task_id = result.id
        self.stdout.write(self.style.SUCCESS(f"Импорт запущен с ID: {result.id}"))

        task_result = AsyncResult(task_id)
        if task_result.ready():
            if task_result.successful():
                self.stdout.write(self.style.SUCCESS("Импорт завершен успешно."))
                shutil.move(path_file, success_dir / path_file.name)
            else:
                self.stdout.write(self.style.ERROR("Импорт завершился с ошибкой."))
                shutil.move(path_file, failed_dir / path_file.name)
        else:
            self.stdout.write("Импорт все еще выполняется...")
