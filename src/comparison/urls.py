from django.urls import path
from .views import ComparisonView

app_name = 'comparison'

urlpatterns = [
    path('add/<int:product_id>/', ComparisonView.as_view(), name='add_to_comparison'),
    path('remove/<int:product_id>/', ComparisonView.as_view(), name='remove_from_comparison'),
    path('', ComparisonView.as_view(), name='get_comparison_list'),
]
