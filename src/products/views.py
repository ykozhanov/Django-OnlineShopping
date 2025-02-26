from typing import Any
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.views import generic
from django.views.generic import ListView
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.views import View
from django.views.generic import DetailView
# from django.core.cache import cache
#
# from .models import ReviewModel
from sellers.models import ProductSeller
from cart.models import Cart, CartItem
from .filter_service import FilterService
from .models import Product
from .forms import ReviewForm
from .services.category_service import CategoryService
from .services.product_service import get_product_cache_service
from .services.cart_service import get_or_create_user_cart, change_or_create_cart_item


def get_cache_key(product_id):
    return f'product_detail_{product_id}'


def load_reviews(request, pk, offset):
    """
    View for loading a batch of reviews for a product
    """
    count_display = 5
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.filter(is_active=True).order_by("-created_at")[offset : offset + count_display]
    review_count = product.reviews.filter(is_active=True).count()
    reviews_data = [
        {
            "username": review.user.username,
            "created_at": review.created_at.strftime('%B %d / %Y / %H:%M'),
            "text": review.text,
            'first_name': review.user.first_name,
            'last_name': review.user.last_name,
        }
        for review in reviews
    ]
    return JsonResponse(
        {
            "reviews": reviews_data,
            "has_more": product.reviews.filter(is_active=True).count() > offset + count_display,
            "review_count": review_count,
        }
    )


def add_review(request, pk):
    """
    View for add new review (use js)
    """
    if request.method == "POST":
        product = get_object_or_404(Product, id=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            review_count = product.reviews.filter(is_active=True).count()
            return JsonResponse(
                {
                    'created_at': review.created_at.strftime('%B %d / %Y / %H:%M'),
                    'text': review.text,
                    'review_count': review_count,
                    'first_name': review.user.first_name,
                    'last_name': review.user.last_name,
                }
            )
        messages.error(request, form.errors)
        return JsonResponse({"errors": form.errors}, status=400)


class SellerDetailView(generic.DetailView):
    """блок «Продавцы» на детальной странице товара"""

    model = Product
    template_name = "products/seller_detail_on_product_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sellers = self.object.sellers.all().select_related("seller")
        sellers_data = []
        for seller in sellers:
            seller_data = {
                "name": seller.seller.name,
                "price": seller.price,
                "delivery_type": seller.get_delivery_type_display(),
                "payment_type": seller.get_payment_type_display(),
            }
            sellers_data.append(seller_data)
        context["sellers_data"] = sellers_data
        return context


class CatalogView(ListView):
    template_name = "products/catalog.html"
    context_object_name = "object_list"
    paginate_by = 8
    single_filters = ("popularity", "avg_price", "reviews", "created_at")
    form_fields = ("in_stock", "free_shipping", "data_to", "data_from", "title")

    def get_queryset(self) -> list[dict[str, Any]]:
        """Получение списка продуктов по категориям из кеша и применение фильтров"""
        self.product_cache_service = get_product_cache_service()
        cached_products = self.product_cache_service.get_products_by_category(category_name=self.kwargs.get("category"))
        return self.apply_filters_and_sort(cached_products)

    def apply_filters_and_sort(self, products: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Устанавливает фильтры из request в self и сортирует products по этим фильтрам"""
        self.sort_params = self.extract_sort_params()
        self.filters_params = self.extract_filters_params(price_range=self.product_cache_service.get_price_range())
        return FilterService.process_products(
            products=products, filter_params=self.filters_params, sort_params=self.sort_params
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """GET запрос возвращает контекст с текущей страницей пагинации"""
        context = super().get_context_data(**kwargs)

        return self.update_context(context=context)

    def create_pagination_context(self, object_list: list[dict[str, Any]]) -> dict[str, Any]:
        """Создает контекст для новой пагинации с первой страницей."""
        paginator = Paginator(object_list=object_list, per_page=self.paginate_by)
        page_number = 1
        page_obj = paginator.get_page(page_number)

        return {"page_obj": page_obj, "object_list": page_obj.object_list, "paginator": paginator}

    def extract_sort_params(self):
        """Извлечение параметров активных фильтров сортировки из request"""
        return {key: value for key, value in self.request.GET.items() if key in self.single_filters}

    def extract_filters_params(self, price_range: dict[str, int]) -> dict[str, Any]:
        """
        Извлечение параметров фильтрации

        request.POST: Извлечение параметров из формы левого фильтра в self.filter_params
        request.GET: Извлечение параметров из GET запроса в self.filter_params
        """
        filter_params = {}
        if self.request.method == "POST":
            if "price" in self.request.POST:
                data_from, data_to = self.request.POST["price"].split(";")
                if int(data_from) != price_range["data_min"]:
                    filter_params["data_from"] = data_from
                if int(data_to) != price_range["data_max"]:
                    filter_params["data_to"] = data_to
            if "title" in self.request.POST and self.request.POST["title"] != "":
                filter_params["title"] = self.request.POST["title"]
            exclude_fields = (
                "data_from",
                "data_to",
                "title",
            )
            request_data = self.request.POST
        else:
            request_data = self.request.GET
            exclude_fields = tuple()
        filter_params.update(self.update_filter_params(request_data=request_data, exclude_fields=exclude_fields))

        return filter_params

    def update_filter_params(self, request_data: dict[str, Any], exclude_fields: tuple[str, ...]) -> dict[str, Any]:
        """Обновление параметров фильтров из request_data"""
        return {k: v for k, v in request_data.items() if k in self.form_fields and k not in exclude_fields}

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Обрабатывает форму левого фильтра, Cоздаёт новый пагинатор и сбрасывает страницу на первую"""
        object_list = self.get_queryset()
        context = self.create_pagination_context(object_list)

        return render(request, self.template_name, self.update_context(context=context))

    def update_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Установка значений фильтров в context, создание строки с параметрами фильтров для возврата на бекенд

        request_params: строка с параметрами фильтров для возврата на бекенд в get запросе
        single_filters: параметры центральных фильтров (сортировка)
        filter_params: параметры левого фильтра (фильтрация)
        """
        context["request_params"] = self.build_filter_query_string()
        context["single_filters"] = self.get_activ_single_filters()
        context.update(self.product_cache_service.get_price_range())
        context.update(self.filters_params)
        context["active_category_list"] = CategoryService.get_active_categories()
        return context

    def build_filter_query_string(self) -> str:
        """Создание строки с параметрами фильтров для возврата на бекенд в get запросе"""
        query_string = "&" + urlencode(self.filters_params, doseq=True)
        query_string += "&" + urlencode(self.sort_params, doseq=True)

        return query_string

    def get_activ_single_filters(self):
        """Получение параметров всех центральных фильтров (сортировка) из request."""
        return {key: self.request.GET.get(key, "") for key in self.single_filters}


class ProductDetailView(DetailView):
    """
    View for display the product detail info
    """
    model = Product
    template_name = 'products/product_detail.html'

    def get_context_data(self, **kwargs):
        """
        Add product seller id, sellers data and price with min values
        """
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        sellers = product.sellers.all()
        if sellers:
            min_price_seller = min(sellers, key=lambda seller: seller.price)
            context['min_price_seller_id'] = min_price_seller.id
            context['min_price_seller_price'] = min_price_seller.price

        sellers = self.object.sellers.all().select_related("seller")
        sellers_data = []
        for seller in sellers:
            seller_data = {
                'id': seller.id,
                "name": seller.seller.name,
                "price": seller.price,
                "delivery_type": seller.get_delivery_type_display(),
                "payment_type": seller.get_payment_type_display(),
            }
            sellers_data.append(seller_data)
        context["sellers_data"] = sellers_data
        return context


class AddProductInCart(View):
    """
    Add product in user cart
    """
    def post(self, request):
        change_or_create_cart_item(request=request)
        return JsonResponse({'success': 'Product added to cart successfully'})


