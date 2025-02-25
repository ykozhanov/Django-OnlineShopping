from django.urls import path
from .views import fake_api_payment

app_name = "paymentapi"

urlpatterns = [
    path("payment/progress", fake_api_payment, name="payment_progress"),
]