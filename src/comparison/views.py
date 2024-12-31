from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from products.models import Product
from .models import ComparisonList


class ComparisonView(LoginRequiredMixin, View):

    @staticmethod
    def get_comparison_list(user):
        comparison_list, created = ComparisonList.objects.get_or_create(user=user)
        return comparison_list

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        comparison_list = self.get_comparison_list(request.user)
        comparison_list.add_product(product)
        return JsonResponse({'message': 'Товар добавлен в список сравнения'})

    def delete(self, request, product_id):
        product = Product.objects.get(id=product_id)
        comparison_list = self.get_comparison_list(request.user)
        comparison_list.remove_product(product)
        return JsonResponse({'message': 'Товар убран из списка сравнения'})

    def get(self, request):
        limit = int(request.GET.get("limit", "3"))
        comparison_list = self.get_comparison_list(request.user)

        context = self.compare_products(comparison_list, limit)
        return render(request, template_name="comparison/comparison.html", context=context)

    @staticmethod
    def compare_products(comparison_list, limit):
        products = comparison_list.get_products(limit)

        if len(products) < 2:
            return {
                "message": 'Недостаточно товаров для сравнения',
                "products": products,
                "comparison_data": {}
            }

        common_characteristics = set(products[0].characteristic_values.keys())
        for product in products[1:]:
            common_characteristics.intersection_update(product.characteristic_values.keys())

        comparison_data = {}
        for characteristic in common_characteristics:
            comparison_data[characteristic] = {product.name: product.characteristics[characteristic] for product in
                                               products}

        return {
            "products": products,
            "comparison_data": comparison_data,
        }
