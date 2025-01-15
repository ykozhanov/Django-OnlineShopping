from django.urls import path
from django.views.generic import TemplateView

from .views import order_step1_view, order_step2_view, order_step3_view, order_step4_view

app_name = "orders"

urlpatterns = [
    path("", order_step1_view, name="orders"),
    path("step2/",order_step2_view, name='orders_step2' ),
    path("step3/", order_step3_view, name='orders_step3'),
    path("step4/", order_step4_view, name='orders_step4'),
]