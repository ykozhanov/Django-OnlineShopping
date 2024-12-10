import logging
from typing import Any

from celery import shared_task
from django.core.cache import cache
from datetime import datetime, timezone

from src.products.models import Product

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def import_products(self, data: list[dict[str, Any]], email: str):
    log_filename = f"import_log_{datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")}.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO)

    if cache.get("import_in_progress"):
        return "Предыдущий импорт ещё не выполнен. Пожалуйста, дождитесь его окончания."

    cache.set("import_in_progress", True)

    try:
        logger.info("Импорт данных начат.")
        # TODO Код импорта
        products = [
            Product(**product)
            for product in data
        ]
        Product.objects.bulk_create(products)
        logger.info("Импорт данных завершен успешно.")
        return "Выполнен"
    except Exception as e:
        logger.error(f"Ошибка при импорте данных: {e}")
        return "Завершён с ошибкой"
    finally:
        cache.delete("import_in_progress")