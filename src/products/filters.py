from collections import defaultdict
from typing import Any, List, Tuple


class FilterService:

    @staticmethod
    def group_and_average(products) -> List[dict[str, Any]]:
        """Группирует данные по product.name и вычисляет среднюю цену для каждой группы"""
        grouped_products = defaultdict(list)
        for product in products:
            grouped_products[product["name"]].append(product)
        result = []
        for name, group in grouped_products.items():
            avg_price = round(sum(product["price"] for product in group) / len(group), 2)
            base_product = group[0]
            base_product["avg_price"] = avg_price
            result.append(base_product)

        return result

    @staticmethod
    def sort_by_keys(keys_for_sort: List[Tuple[str, bool]], products: List[dict[str, Any]]) -> List[dict[str, Any]]:
        for key, reverse_flag in reversed(keys_for_sort):
            products.sort(key=lambda x: x.get(key), reverse=reverse_flag)
        return products

    @staticmethod
    def filter_products(filters, products):
        """Фильтрует данные по заданным параметрам"""
        if "data_from" in filters:
            filters["data_from"] = float(filters["data_from"])
        if "data_to" in filters:
            filters["data_to"] = float(filters["data_to"])
        filtered_products = []
        for product in products:
            if (
                ("in_stock" not in filters or product["quantity"] > 0)
                and ("free_shipping" not in filters or product["delivery_type"] == "FREE")
                and ("data_from" not in filters or product["price"] >= filters["data_from"])
                and ("data_to" not in filters or product["price"] <= filters["data_to"])
                and ("title" not in filters or product["name"].lower().find(filters["title"].lower()) != -1)
            ):
                filtered_products.append(product)

        return filtered_products

    @staticmethod
    def process_products(products, keys_for_sort, filters):
        """Вызов функций фильтрации, сортировки и группировки"""
        filtered_products = FilterService.filter_products(filters=filters, products=products)
        grouped_products = FilterService.group_and_average(products=filtered_products)

        return FilterService.sort_by_keys(keys_for_sort=keys_for_sort, products=grouped_products)
