from django.urls import path

from .views import add_review, load_reviews, ProductDetailView

urlpatterns = [
    path('<int:pk>/',ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/add_review/', add_review, name='add_review'),
    path('load_reviews/<int:pk>/<int:offset>/', load_reviews, name='load_reviews'),
]
