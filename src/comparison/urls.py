from django.urls import path
from .views import ComparisonView

app_name = 'comparison'

urlpatterns = [
    path('', ComparisonView.as_view(), name='comparison'),
    path('add/<int:product_id>/', ComparisonView.as_view(), name='comparison_add'),
    path('delete/<int:product_id>/', ComparisonView.as_view(), name='comparison_delete'),
]
