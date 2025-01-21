from django.urls import path

from .views import order_step1_view

app_name = "orders"

urlpatterns = [
    path("", order_step1_view, name="orders"),
]