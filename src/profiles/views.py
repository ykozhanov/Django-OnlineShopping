from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render
from django.views.generic import CreateView, DetailView
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, CustomLoginForm, CustomSetPasswordForm, CustomPasswordResetForm, CustomUserEditForm

User = get_user_model()


class UserProfileView(LoginRequiredMixin, DetailView):
    """
    View for display the profile of the currently logged-in user
    """
    model = User

    def get_object(self):
        """
        Returns the currently logged-in user
        """
        return self.request.user


@login_required
def user_profile_edit_view(request):
    """
    View for editing the user profile
    """
    user = request.user
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, request.FILES, instance=user)
        form.request = request
        if form.is_valid():
            form.save()
            return render(request, 'profiles/user_detail_edit.html', context={'form':form, 'user': user})
    else:
        form = CustomUserEditForm(initial={'phone_number': user.phone_number})
    return render(request, 'profiles/user_detail_edit.html', context={'form':form, 'user':user})


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
