from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import DetailView
from .forms import CustomUserEditForm

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

