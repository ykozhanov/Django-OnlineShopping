from django.urls import path
from django.views.generic import TemplateView

from .views import (
    UserRegistrationView, 
    CustomLoginView, 
    CustomPasswordResetView, 
    CustomPasswordResetConfirmView, 
    UserProfileView, 
    user_profile_edit_view,
    CustomLogoutView,
    UserProductHistoryView
)

app_name = "profiles"

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', TemplateView.as_view(template_name='login/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', TemplateView.as_view(template_name='login/password_reset_complete.html'), name='password_reset_complete'),

    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/edit/', user_profile_edit_view, name='profile_edit'),
    path('profile/product_history/', UserProductHistoryView.as_view(), name='product_history')
]