from django.urls import path

from .views import HomepageTemplateView

app_name = "homepage"

urlpatterns = [
    path("", HomepageTemplateView.as_view(), name="index"),
]