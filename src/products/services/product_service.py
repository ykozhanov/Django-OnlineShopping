from typing import Dict, Any, List, Union

from django.core.cache import cache
from django.db.models import Min, Max, F, QuerySet

from megano import settings
from products.services.category_service import CategoryService
from sellers.models import ProductSeller


def get_product_cache_service():
    return ProductCacheService()


class ProductCacheService:
    def __init__(self):
        self.max_price = 0
        self.min_price = 0

    def get_price_range(self):
        return {"data_min": self.min_price, "data_max": self.max_price}

    def get_products_from_db(self, category_name: str) -> Union[QuerySet[Dict[str, any]], list]:
        """Получает products из базы данных по имени категории."""
        queryset = (
            ProductSeller.objects.filter(
                seller__is_active=True,
                product__is_active=True,
                product__category__is_active=True,
                product__category__name=category_name,
            )
            .annotate(
                name=F("product__name"),
                image=F("product__image"),
                category=F("product__category__name"),
                category_parent=F("product__category__parent__name"),
                created_at=F("product__created_at"),
            )
            .values(
                "id",
                "image",
                "name",
                "category",
                "category_parent",
                "created_at",
                "price",
                "delivery_type",
                "quantity",
            )
        )
        return queryset

    def cache_products_by_category(self, category_name: str) -> Dict[str, Any]:
        """
        Получает с базы данных products по имени категории, высчитывает часто используемые параметры
        и сохраняет в кэш вместе с products.
        """
        cache_key = f"products_in_category_{category_name}"
        cached_data = cache.get(cache_key)
        if cached_data is None:
            products_queryset = self.get_products_from_db(category_name)
            if len(products_queryset):
                aggregation = products_queryset.aggregate(min_price=Min("price"), max_price=Max("price"))
            else:
                aggregation = {"min_price": None, "max_price": None}

            cached_data = {
                "products": list(products_queryset),
                "min_price": aggregation["min_price"],
                "max_price": aggregation["max_price"],
            }

            cache.set(cache_key, cached_data, timeout=settings.PRODUCT_CACHE_TIMEOUT)

        return cached_data

    def merge_products_categories(self, products_in_categories: list) -> List[Dict[str, Any]]:
        """Объединяет products из разных категорий"""
        merged_category_data = []
        for category in products_in_categories:
            merged_category_data.extend(category["products"])
        self.min_price = min(filter(None, (category["min_price"] for category in products_in_categories)), default=0)
        self.max_price = max(filter(None, (category["max_price"] for category in products_in_categories)), default=0)

        return merged_category_data

    def get_products_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Возвращает кэшированные список products из входящей категории и её наследников"""
        all_categories = CategoryService.get_active_categories()
        category = [category for category in all_categories if category.name == category_name]
        if category:
            categories = CategoryService.get_childrens_by_parent(parent=category[0])
            categories_with_products = [self.cache_products_by_category(category.name) for category in categories]

            return self.merge_products_categories(categories_with_products)

        return []
