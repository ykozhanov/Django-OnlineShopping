from django.urls import path

from .views import ProductDetailView, add_review

urlpatterns = [
    path("product/<int:pk>/", ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:pk>/add_review/', add_review, name='add_review'),
]
