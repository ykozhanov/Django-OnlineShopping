from django.urls import path

from .views import (
    add_review,
    load_reviews,
    SellerDetailView,
    CatalogView,
    ProductDetailView,
    AddProductInCart,
)

app_name = "products"

urlpatterns = [
    path("product/<int:pk>/add_review/", add_review, name="add_review"),
    path("load_reviews/<int:pk>/<int:offset>/", load_reviews, name="load_reviews"),
    path("sellers/<int:pk>/", SellerDetailView.as_view(), name="seller_detail"),
    path('category/<str:category>/catalog/', CatalogView.as_view(), name='catalog'),
    path('product/<int:pk>/add_review/', add_review, name='add_review'),
    path('addproduct/', AddProductInCart.as_view(), name='addproduct')
]
