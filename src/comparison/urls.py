from django.urls import path
from .views import ComparisonView, ComparisonAPIView

app_name = 'comparison'

urlpatterns = [
    path('', ComparisonView.as_view(), name='comparison'),
    path('api/get/', ComparisonAPIView.as_view(), name='comparison_get'),
    path('api/add/<int:product_id>/', ComparisonAPIView.as_view(), name='comparison_add'),
    path('api/delete/<int:product_id>/', ComparisonAPIView.as_view(), name='comparison_delete'),
]
