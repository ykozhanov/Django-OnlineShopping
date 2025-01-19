from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.views import View
from products.models import Product, Category


class ProductsForCategoryView(View):
    """Возвращает products по установленной category при смене категории"""

    def get(self, request: WSGIRequest, category_id: int) -> JsonResponse:
        if category_id == 0:
            products = Product.objects.all()
        else:
            category = Category.objects.get(id=category_id)
            descendants = category.get_descendants()
            products = Product.objects.filter(category_id__in=[category_id] + [d.id for d in descendants])
        return JsonResponse({"products": list(products.values("id", "name"))})
