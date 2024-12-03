from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, CustomLoginForm

User = get_user_model()


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "login/login.html"
    # success_url = reverse_lazy("home")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['email'].widget.attrs.update({
            'class': 'user-input',
            'placeholder': 'E-mail',
        })
        form.fields['password'].widget.attrs.update({
            'placeholder': '*********',
        })
        return form


class UserRegistrationView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = "login/registr.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)