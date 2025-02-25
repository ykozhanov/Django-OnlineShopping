from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from django.http import HttpRequest

from products.models import Product


class ComparisonService:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def add_product(self, product_id: int) -> None:
        get_object_or_404(Product, id=product_id)
        comparison_list: list[int] = self.request.session.get('comparison_list', [])

        if product_id not in comparison_list:
            comparison_list.append(product_id)
            self.request.session['comparison_list'] = comparison_list

    def remove_product(self, product_id: int) -> None:
        comparison_list: list[int] = self.request.session.get('comparison_list', [])

        if product_id in comparison_list:
            comparison_list.remove(product_id)
            self.request.session['comparison_list'] = comparison_list

    def get_products(self, limit: int = 3) -> QuerySet[Product]:
        if limit is None:
            limit = 3
        comparison_list = self.request.session.get('comparison_list', [])
        return Product.objects.filter(id__in=comparison_list)[:limit]

    def get_product_count(self) -> int:
        return len(self.request.session.get('comparison_list', []))
