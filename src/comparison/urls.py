from django.urls import path
from .views import ComparisonView

app_name = 'comparison'

urlpatterns = [
    path('', ComparisonView.as_view(), name='comparison'),
]
