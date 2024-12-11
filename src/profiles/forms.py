from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'user-input', 'placeholder': 'Имя'})
        self.fields['email'].widget.attrs.update({'class': 'user-input', 'placeholder': 'E-mail'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Пароль'})
        self.fields.pop('password2', None)
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

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'user-input', 'placeholder': 'E-mail'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Пароль'})
        self.fields.pop('username', None)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError("Неверный email.")

            if not user.check_password(password):
                raise forms.ValidationError("Неверный пароль.")

            self.cleaned_data['user'] = user
        return self.cleaned_data


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({
            "class": "user-input",
            "placeholder": "E-mail",
        })


class CustomSetPasswordForm(SetPasswordForm):
    # code = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Код'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update({
            "placeholder": "Пароль",
        })
        self.fields.pop("new_password2", None)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        if not new_password1:
            raise forms.ValidationError("Пароль не может быть пустым.")
        return cleaned_data