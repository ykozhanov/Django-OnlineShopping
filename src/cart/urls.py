from django.urls import path
from .views import CartView, update_cart_item

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('update/<intLitem_id>/<str:action>/', update_cart_item, name='update_cart_item'),
]