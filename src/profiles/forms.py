from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django import forms

from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)


# class CustomUserChangeForm1(UserChangeForm): удалить нужно будет
#
#     class Meta:
#         model = User
#         fields = ('last_name','email', 'avatar', 'phone_number', 'password', 'first_name')
#
#     password_reply = forms.CharField(widget=forms.PasswordInput)
#
#
#     def clean(self):
#         cleaned_data = super().clean()
#         last_name = cleaned_data.get('last_name', '')
#
#         if not last_name:
#             self.add_error('last_name', 'Last name is required')
#             return
#
#         parts = last_name.split()
#         if len(parts) < 2:
#             self.add_error('first_name', 'First name is required')
#             return
#
#         cleaned_data['last_name'] = parts[0]
#         cleaned_data['first_name'] = parts[1]
#         print('self.clean', self.cleaned_data)
#         print(self.cleaned_data.get('password_reply', 'no no no no'))
#
#         return cleaned_data

class CustomUserChangeForm2(UserChangeForm):

    class Meta:
        model = User
        fields = ('last_name','email', 'avatar', 'first_name')

    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_reply = forms.CharField(widget=forms.PasswordInput, required=False)
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'phone-mask'}), required=False)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        cleaned_number = ''.join(c for c in phone_number if c.isdigit())[1:]

        print(cleaned_number, 'cleaned number')


        if len(cleaned_number) != 10:
            raise forms.ValidationError('Invalid phone number format')

        return cleaned_number


    def clean(self):
        cleaned_data = super().clean()
        last_name = cleaned_data.get('last_name', '')

        if not last_name:
            self.add_error('last_name', 'Last name is required')
        else:
            parts = last_name.split()
            cleaned_data['last_name'] = parts[0]
            if len(parts) < 2:
                self.add_error('first_name', 'First name is required')
            else:
                cleaned_data['first_name'] = parts[1]

        password = cleaned_data.get('password', '')
        password_reply = cleaned_data.get('password_reply', '')


        print(password, password_reply)

        if password != password_reply:
            self.add_error('password_reply', 'Passwords do not match.')

        return cleaned_data