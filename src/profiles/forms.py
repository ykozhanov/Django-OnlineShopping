from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # self.fields['username'].widget.attrs.update({'class': 'user-input', 'placeholder': 'Имя'})
        self.fields['email'].widget.attrs.update({'class': 'user-input', 'placeholder': 'E-mail'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Пароль'})
        # self.fields['password2'].widget.attrs.update({'placeholder': 'Повторите пароль'})


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)


class CustomLoginForm(AuthenticationForm):
    email = forms.EmailField(label='E-mail')

    class Meta:
        model = User
        fields = ['email', 'password']

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("Пользователь с таким адресом электронной почты не найден.")

            if not user.check_password(password):
                raise forms.ValidationError("Неверный пароль.")

            self.cleaned_data['user'] = user
        return self.cleaned_data