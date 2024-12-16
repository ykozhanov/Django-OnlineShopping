from django.urls import path

from .views import UserProfileView, user_profile_edit_view

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/edit/', user_profile_edit_view, name='profile_edit')
]
