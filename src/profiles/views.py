from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import DetailView
from .forms import CustomUserChangeForm2

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
    form = CustomUserChangeForm2()
    if request.method == 'GET':
        return render(request, 'profiles/user_detail_edit.html', context={'user': user, 'form':form})
    print(request.POST)
    form = CustomUserChangeForm2(request.POST)
    print(dict(form.errors.items()))
    print(form.cleaned_data)
    if form.is_valid():
        print('RURURURUURURU')
    return render(request, 'profiles/user_detail_edit.html', context={'user': user, 'form':form})
