from datetime import datetime, timedelta

from django.core.cache import cache
from django.utils import timezone

from megano.settings import PRODUCT_CACHE_TIMEOUT
from products.models import Product


class DayOfferService:
    """
    Класс с функционалом получения и кэширования
    рандомного товара с ограниченным тиражом
    """

    @classmethod
    def _get_random_product_from_db(cls) -> Product | None:
        """Возвращает рандомный товар ограниченного тиража"""
        day_offer_product = Product.objects.filter(
            is_active=True, limited_edition=True
        ).prefetch_related('sellers').select_related('category').order_by('?').first()
        return day_offer_product
    
    @classmethod
    def update_random_product(cls) -> tuple:
        """
        Выбирает новый товар при истечении срока кэша
        Для периодической задачи celery
        """
        day_offer_product: Product | None = cls._get_random_product_from_db()
        if day_offer_product:
            updated_at = timezone.now()
            cache.set('random_product', day_offer_product)
            cache.set('random_product_updated_at', updated_at.timestamp())
            return day_offer_product, updated_at.timestamp()
        return None, None

    @classmethod
    def get_random_product(cls) -> dict:
        """Возвращаект текущий рандомный товар с временем его нахождения в предложении дня"""
        day_offer_product = cache.get('random_product')
        updated_at_timestamp = cache.get('random_product_updated_at')

        if not (day_offer_product or updated_at_timestamp):
            # Актуально для первого запуска
            day_offer_product, updated_at_timestamp = cls.update_random_product()
        if not (day_offer_product or updated_at_timestamp):
                day_offer_product = None
                finished_at = None
        else:
            
            finished_at = timezone.datetime.fromtimestamp(updated_at_timestamp, tz=timezone.utc) + timedelta(days=2)
            print(finished_at)
        return {
            'day_offer_product': day_offer_product,
            'finished_at': finished_at,
        }