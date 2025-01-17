from typing import Any

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from products.models import Product


class ComparisonView(LoginRequiredMixin, View):

    def post(self, request: HttpRequest, product_id: int) -> JsonResponse:
        product = get_object_or_404(Product, id=product_id)
        comparison_list: list[int] = request.session.get('comparison_list', [])
        if product_id not in comparison_list:
            comparison_list.append(product_id)
        request.session['comparison_list'] = comparison_list
        return JsonResponse({'message': 'Товар добавлен в список сравнения'})

    def delete(self, request: HttpRequest, product_id: int) -> JsonResponse:
        comparison_list: list[int] = request.session.get('comparison_list', [])
        if product_id in comparison_list:
            index = comparison_list.index(product_id)
            comparison_list.pop(index)
        request.session['comparison_list'] = comparison_list
        return JsonResponse({'message': 'Товар убран из списка сравнения'})

    def get(self, request) -> JsonResponse:
        limit = int(request.GET.get("limit", "3"))
        comparison_list: list[int] = request.session.get('comparison_list', [])

        context = self._compare_products(comparison_list, limit)
        return render(request, template_name='comparison/comparison.html', context=context)

    @staticmethod
    def _compare_products(comparison_list: list[int], limit: int) -> dict[str, QuerySet | dict[str, Any]]:
        products: QuerySet[Product] = Product.objects.filter(id__in=comparison_list)[:limit]
        if len(products) < 2:
            return {
                'message': 'Недостаточно товаров для сравнения',
                'products': products,
                'comparison_data': {},
            }

        common_characteristics = set(products[0].characteristic_values.keys())
        for product in products[1:]:
            common_characteristics.intersection_update(product.characteristic_values.keys())

        comparison_data = {}
        for characteristic in common_characteristics:
            comparison_data[characteristic] = {product.name: product.characteristics[characteristic] for product in
                                               products}

        return {
            'products': products,
            'comparison_data': comparison_data,
        }


def get_len_comparison(request: HttpRequest) -> JsonResponse:
    if request.method == 'GET':
        comparison_list: list[int] = request.session.get('comparison_list', [])
        return JsonResponse({'count': len(comparison_list)})
