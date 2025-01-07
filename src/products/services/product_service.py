from typing import Dict, Any, List, Union

from django.core.cache import cache
from django.db.models import Min, Max, F, QuerySet

from sellers.models import ProductSeller


def get_product_cache_service(category_service):
    return ProductCacheService(category_service=category_service)


class ProductCacheService:
    def __init__(self, category_service):
        self.category_service = category_service
        self.max_price = 0
        self.min_price = 0

    def get_min_price(self):
        return self.min_price

    def get_max_price(self):
        return self.max_price

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
                aggregation = {"min_price": 0, "max_price": 0}

            cached_data = {
                "products": list(products_queryset),
                "min_price": aggregation["min_price"],
                "max_price": aggregation["max_price"],
            }

            cache.set(cache_key, cached_data, timeout=60 * 60 * 24)

        return cached_data

    def merge_products_categories(self, products_in_categories: list) -> List[Dict[str, Any]]:
        """Объединяет products из разных категорий"""
        merged_category_data = []
        for category in products_in_categories:
            merged_category_data.extend(category["products"])
        self.min_price = min(category["min_price"] for category in products_in_categories)
        self.max_price = max(category["max_price"] for category in products_in_categories)

        return merged_category_data

    def get_products_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Возвращает кэшированные список products из входящей категории и её наследников"""
        all_categories = self.category_service.get_active_categories()
        category = [category for category in all_categories if category.name == category_name]
        if category:
            categories = self.category_service.get_childrens_by_parent(parent=category[0])
            categories_with_products = [self.cache_products_by_category(category.name) for category in categories]

            return self.merge_products_categories(categories_with_products)

        return []
