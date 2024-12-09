from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import DetailView

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



def user_profile_edit(request):
    user = request.user
    if request.method == 'GET':
        return render(request, 'profiles/user_detail_edit.html', context={'user': user})
    print(request.POST)
    return render(request, 'profiles/user_detail_edit.html', context={'user': user})
