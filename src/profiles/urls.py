from django.urls import path

from .views import UserRegistrationView, CustomLoginView

app_name = "profiles"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
]