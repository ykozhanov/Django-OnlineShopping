from django.urls import path

from .views import ProductDetailView, add_review, load_reviews
urlpatterns = [
    path("product/<int:pk>/", ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:pk>/add_review/', add_review, name='add_review'),
    path('load_reviews/<int:pk>/<int:offset>/', load_reviews, name='load_reviews'),
]
