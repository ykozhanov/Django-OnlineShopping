from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.views.generic import CreateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, CustomLoginForm, CustomSetPasswordForm, CustomPasswordResetForm

User = get_user_model()


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "login/login.html"
    # TODO Добавить success_url
    # success_url = reverse_lazy("home")


class UserRegistrationView(CreateView):
    # model = User
    form_class = CustomUserCreationForm
    template_name = "login/registr.html"
    # TODO Изменить на home
    success_url = reverse_lazy("profiles:login")


class CustomPasswordResetView(PasswordResetView):
    template_name = "login/password_reset.html"
    success_url = reverse_lazy("profiles:password_reset_done")
    email_template_name = "login/password_reset_email.html"
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "login/password_reset_confirm.html"
    success_url = reverse_lazy("profiles:password_reset_complete")
    form_class = CustomSetPasswordForm
