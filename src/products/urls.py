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
    path('<int:pk>/',ProductDetailView.as_view(), name='product_detail'),
    path("product/<int:pk>/add_review/", add_review, name="add_review"),
    path("load_reviews/<int:pk>/<int:offset>/", load_reviews, name="load_reviews"),
    path("sellers/<int:pk>/", SellerDetailView.as_view(), name="seller_detail"),
    path('category/<str:category>/catalog/', CatalogView.as_view(), name='catalog'),
    path('addproduct/', AddProductInCart.as_view(), name='addproduct'),
    path('<int:pk>', ProductDetailView.as_view(), name='detail_view'),
]
