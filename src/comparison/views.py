from typing import Any

from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from products.models import Product
from .services import ComparisonService


def compare_products(products: QuerySet[Product]) -> dict[str, QuerySet | dict[str, Any]]:
    if products:
        common_characteristics = set(products[0].characteristic_values.keys())
        for product in products[1:]:
            common_characteristics.intersection_update(product.characteristic_values.keys())
        comparison_data = {}
        for characteristic in common_characteristics:
            comparison_data[characteristic] = {
                product.name: product.characteristics[characteristic]
                for product in products
            }
    else:
        comparison_data = products
    return {
        'products': products,
        'comparison_data': comparison_data,
    }


class ComparisonView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest) -> JsonResponse:
        cs = ComparisonService(request)
        limit = int(request.GET.get("limit", "3"))
        products = cs.get_products(limit)
        context = compare_products(products)
        return render(request, template_name='comparison/comparison.html', context=context)
