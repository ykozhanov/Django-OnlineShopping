from django.urls import path
from . import views

urlpatterns = [
    path('get_products_for_category/<int:category_id>/',
         views.get_products_for_category,
         name='get_products_for_category'),
]