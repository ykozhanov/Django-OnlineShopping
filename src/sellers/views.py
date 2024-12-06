from django.http import JsonResponse

from products.models import Product, Category


def get_products_for_category(request, category_id):
    """возвращает products по установленной category при смене категории"""
    if category_id == 0:
        products = Product.objects.all().values('id', 'name')
    else:
        category = Category.objects.get(id=category_id)
        descendants = category.get_descendants()
        products = Product.objects.filter(
            category_id__in=[category_id] + [d.id for d in descendants]).values('id', 'name')
    return JsonResponse({'products': list(products)})

