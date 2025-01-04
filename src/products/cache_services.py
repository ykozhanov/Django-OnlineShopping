from typing import Dict, Any, List

from django.core.cache import cache
from django.db.models import Min, Max, F

from products.models import Category
from sellers.models import ProductSeller


class ProductCacheService:
    def __init__(self):
        self.max_price = 0
        self.min_price = 0

    def get_products_from_db(self, category_name):
        """Получает продукты из базы данных по имени категории."""
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

    def cache_products_by_category(self, category_name):
        """
        Получает с базы данных продукты по имени категории, высчитывает часто используемые параметры и сохраняет в кэш.
        """
        cache_key = f"products_in_category_{category_name}"
        cached_data = cache.get(cache_key)
        if cached_data is None:
            products_queryset = self.get_products_from_db(category_name)
            aggregation = products_queryset.aggregate(min_price=Min("price"), max_price=Max("price"))

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

    def get_products_by_category(self, category_name: str = None) -> List[Dict[str, Any]]:
        """Возвращает кэшированные список products из входящей категории и её наследников"""
        if not category_name:
            categories_with_products = Category.objects.filter(products__isnull=False).distinct()
            categories = [category for category in categories_with_products]
        else:
            categories = Category.objects.get(name=category_name)
        categories_with_products = [self.cache_products_by_category(category.name) for category in categories]

        return self.merge_products_categories(categories_with_products)
