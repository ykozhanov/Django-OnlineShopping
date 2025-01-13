from django.urls import path
from .views import CartView, update_cart_item

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('update/<int:item_id>/<str:action>/', update_cart_item, name='update_cart_item'),
]