import logging
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

from celery import shared_task
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.conf import settings

from src.products.models import Product

logger = logging.getLogger("import_logger")
formatter = logging.Formatter("%(levelname)s %(asctime)s %(module)s %(message)s")


def send_email(subject: str, message: str, recipient_list: list[str], path_file: str | Path):
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipient_list,
    )
    email.attach_file(path=path_file)
    email.send(fail_silently=False)



@shared_task(bind=True)
def import_products(self, data: list[dict[str, Any]], email: str):
    log_file: Path = settings.BASE_DIR / "importapp" / "logs" / f"import_log_{datetime.now(tz=timezone.utc).strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(filename=log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if cache.get("import_in_progress"):
        return "Предыдущий импорт ещё не выполнен. Пожалуйста, дождитесь его окончания."

    cache.set("import_in_progress", True)

    try:
        logger.info("Импорт данных начат.")
        products = [
            Product(**product)
            for product in data
        ]
        for product in products:
            try:
                product.save()
                logger.info(f"Успешно добавлен товар: {product.name!r}.")
            except Exception as e:
                logger.error(f"Ошибка при импорте {product.name!r}: {e}.")
        logger.info("Импорт данных завершен успешно.")
        return "Выполнен"
    except Exception as e:
        logger.error(f"Ошибка при импорте данных: {e}")
        return "Завершён с ошибкой"
    finally:
        cache.delete("import_in_progress")
        send_email(
            subject="Отчёт об импорте.",
            message="Прикрепили лог-файл об импорте ниже.",
            recipient_list=[email],
            path_file=log_file,
        )
