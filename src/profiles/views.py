from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import DetailView

User = get_user_model()

# Create your views here.

class UserProfile(LoginRequiredMixin, DetailView):
    model = User

    def get_object(self):
        return self.request.user