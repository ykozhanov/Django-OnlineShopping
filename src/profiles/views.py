from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import DetailView
from .forms import CustomUserChangeForm2
from django.contrib import messages

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
    if request.method == 'POST':
        print(request.POST)
        form = CustomUserChangeForm2(request.POST, request.FILES, instance=user)
        form.request = request
        print(form.changed_data, 'change')
        print(dict(form.errors.items()))
        messages.success(request, 'Профиль успешно сохранен')
        if form.is_valid():
            form.save()
            return render(request, 'profiles/user_detail_edit.html', context={'form':form, 'user': user})
    else:
        form = CustomUserChangeForm2(initial={'phone_number': user.phone_number})

    return render(request, 'profiles/user_detail_edit.html', context={'form':form, 'user':user})

