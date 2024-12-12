from django.contrib.auth import authenticate, login, update_session_auth_hash
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


class CustomUserChangeForm2(UserChangeForm):

    class Meta:
        model = User
        fields = ('last_name','email', 'avatar', 'first_name', 'phone_number')

    password = forms.CharField(widget=forms.PasswordInput, required=False)
    password_reply = forms.CharField(widget=forms.PasswordInput, required=False)
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'phone-mask'}), required=False)

    def clean_phone_number(self):
        """
        Validates and cleans the phone number field.
        """

        phone_number = self.cleaned_data['phone_number']
        if phone_number:
            cleaned_number = ''.join(c for c in phone_number if c.isdigit())[1:]

            if len(cleaned_number) != 10:
                raise forms.ValidationError('Invalid phone number format')

            return cleaned_number


    def clean(self):
        """
        Cleans and validates the form data:
        1. Ensures that the last name is provided.
        2. Splits the last name into first name and last name if both are provided in the last name field.
        3. Ensures that the password and password_reply fields match.
        """
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

        if password != password_reply:
            self.add_error('password_reply', 'Passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        """
        Saves the form data and updates the user's session if the password is changed.
        """
        user = super().save(commit=False)
        password = self.cleaned_data.get('password', None)
        if password:
            user.set_password(password)
        if commit:
            user.save()
            update_session_auth_hash(self.request, user)
        return user