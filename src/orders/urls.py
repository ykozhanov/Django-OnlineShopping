from django.urls import path
from django.views.generic import TemplateView

from .views import orderview

app_name = "orders"

urlpatterns = [
    path("", orderview, name="orders")
]