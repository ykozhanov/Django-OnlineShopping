from django.urls import path
from django.views.generic import TemplateView

from .views import fake_api_payment

app_name = "fakeapi"

urlpatterns = [
    path("payment/progress", fake_api_payment, name="payment_progress"),
]