from django.urls import path
from .views import ProductsForCategoryView

app_name = "sellers"

urlpatterns = [
    path(
        "get_products_for_category/<int:category_id>/",
        ProductsForCategoryView.as_view(),
        name="get_products_for_category",
    ),
]
