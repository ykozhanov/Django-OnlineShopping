from django.urls import path

from .views import DiscountListView

app_name = "discounts"

urlpatterns = [
    path('',DiscountListView.as_view(), name='discount_list'),
]
