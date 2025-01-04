from typing import Any, Dict
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.views import generic
from django.views.generic import ListView

from .cache_services import ProductCacheService
from .filters import FilterService
from .models import Product
from .forms import ReviewForm


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
            "created_at": review.created_at.strftime("%B %d / %Y / %H:%M"),
            "text": review.text,
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
                    "username": review.user.username,
                    "created_at": review.created_at.strftime("%B %d / %Y / %H:%M"),
                    "text": review.text,
                    "review_count": review_count,
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
    paginate_by = 3
    single_filters = ("popularity", "avg_price", "reviews", "created_at")
    form_fields = ("in_stock", "free_shipping", "data_to", "data_from", "title")

    def __init__(self):
        super().__init__()
        self.product_cache_service = ProductCacheService()
        self.filter_params = dict()
        self.sort_params = dict()

    def get_queryset(self) -> list[dict[str, Any]]:
        """Получение списка продуктов по категориям из кеша и применение фильтров"""
        cached_data = self.product_cache_service.get_products_by_category()
        filters = self.fetch_filter_params()
        keys_for_sort = self.get_sort_keys()

        return FilterService.process_products(products=cached_data, keys_for_sort=keys_for_sort, filters=filters)

    def get_sort_keys(self) -> list[tuple[str, bool]]:
        """Получение параметров сортировки из GET запроса и создание ключей сортировки с возможностью реверса"""
        self.sort_params = {key: value for key, value in self.request.GET.items() if key in self.single_filters}
        keys_for_sort = []
        for key, value in self.sort_params.items():
            if key in ("popularity", "reviews"):
                continue
            reverse = False if value == "desc" else True
            keys_for_sort.append((key, reverse))
        return keys_for_sort

    def fetch_filter_params(self) -> dict[str, Any]:
        """
        Извлечение параметров фильтрации

        request.POST: Извлечение параметров из формы левого фильтра в self.filter_params
        request.GET: Извлечение параметров из GET запроса в self.filter_params
        """
        if self.request.method == "POST":
            data_from, data_to = self.request.POST["price"].split(";")
            if int(data_from) != self.product_cache_service.min_price:
                self.filter_params["data_from"] = data_from
            if int(data_to) != self.product_cache_service.max_price:
                self.filter_params["data_to"] = data_to
            if "title" in self.request.POST and self.request.POST["title"] != "":
                self.filter_params["title"] = self.request.POST["title"]
            exclude_fields = ("data_from", "data_to", "title")
            self.update_filter_params(request_data=self.request.POST, exclude_fields=exclude_fields)
        elif self.request.method == "GET":
            self.update_filter_params(request_data=self.request.GET, exclude_fields=[])

        return self.filter_params

    def update_filter_params(self, request_data, exclude_fields):
        """Обновление параметров фильтров из request_data"""
        self.filter_params.update(
            {k: v for k, v in request_data.items() if k in self.form_fields and k not in exclude_fields}
        )

    def get_context_data(self, **kwargs):
        """
        get запрос возвращает контекст с текущей страницей пагинации
        post запрос создаёт новый пагинатор и сбрасывает страницу на первую
        """
        if self.request.method == "POST":
            object_list = self.get_queryset()
            context = self.create_pagination_context(object_list)
        else:
            context = super().get_context_data(**kwargs)

        return self.update_context(context=context)

    def create_pagination_context(self, object_list: list[dict[str, Any]]) -> dict[str, Any]:
        """Создает контекст для новой пагинации с первой страницей."""
        paginator = Paginator(object_list=object_list, per_page=self.paginate_by)
        page_number = 1
        page_obj = paginator.get_page(page_number)

        return {"page_obj": page_obj, "object_list": page_obj.object_list, "paginator": paginator}

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data(**kwargs)

        return render(request, self.template_name, context)

    def update_context(self, context) -> Dict[str, Any]:
        """
        Установка значений фильтров в context, создание строки с параметрами фильтров для возврата на бекенд

        request_params: строка с параметрами фильтров для возврата на бекенд в get запросе
        single_filters: параметры центральных фильтров (сортировка)
        self.filter_params: параметры левого фильтра (фильтрация)
        """
        context["request_params"] = "&" + urlencode(self.filter_params) if self.filter_params else ""
        context["request_params"] += "&" + urlencode(self.sort_params) if self.sort_params else ""
        single_filters = {key: self.request.GET[key] if key in self.request.GET else "" for key in self.single_filters}
        context["single_filters"] = single_filters
        context["data_min"] = self.product_cache_service.min_price
        context["data_max"] = self.product_cache_service.max_price
        context.update(self.filter_params)

        return context
