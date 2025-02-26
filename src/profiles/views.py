from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, LogoutView
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, TemplateView
from django.urls import reverse_lazy
from products.models import ViewHistory

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        latest_order = user.orders.order_by('-created_at').first()
        context.update({'order': latest_order})
        return context


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
    success_url = reverse_lazy("homepage:index")
    
    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        login(self.request, user)
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("profiles:login")
    

class UserRegistrationView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "login/registr.html"
    success_url = reverse_lazy("login")


class CustomPasswordResetView(PasswordResetView):
    template_name = "login/password_reset.html"
    success_url = reverse_lazy("profiles:password_reset_done")
    email_template_name = "login/password_reset_email.html"
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "login/password_reset_confirm.html"
    success_url = reverse_lazy("profiles:password_reset_complete")
    form_class = CustomSetPasswordForm

class UserProductHistoryView(TemplateView):
    """
    View to display the User's Product History
    """
    template_name = 'profiles/user_product_history.html'
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        user = request.user
        history_products = (ViewHistory.objects.filter(user=user)
                            .select_related('product__category')
                            .prefetch_related('product__sellers').all())
        context['history_products'] = history_products
        return self.render_to_response(context)
