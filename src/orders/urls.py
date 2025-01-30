from django.urls import path

from .views import (
    OrderStepOneView,
    OrderStepTwoView,
    OrderStepThreeView,
    OrderStepFourView,
    OrderPaymentView,
    OrderPaymentProgressView,
    OrdersHistoryList,
    OrdersHistoryDetail,
)

app_name = "orders"

urlpatterns = [
    path("", OrderStepOneView.as_view(), name="orders"),
    path("step2/", OrderStepTwoView.as_view(), name='orders_step2'),
    path("step3/", OrderStepThreeView.as_view(), name='orders_step3'),
    path("step4/", OrderStepFourView.as_view(), name='orders_step4'),
    path('payment/', OrderPaymentView.as_view(), name='payment'),
    path('payment/progress/', OrderPaymentProgressView.as_view(), name='payment_progress'),
    path('history/', OrdersHistoryList.as_view(), name='orders_history_list'),
    path('history/<int:id>/', OrdersHistoryDetail.as_view(), name='orders_history_detail'),
]
