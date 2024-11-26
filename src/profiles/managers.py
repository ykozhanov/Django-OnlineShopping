from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Пользовательский менеджер моделей, где уникальным
    идентификатором для аутентификации является электронная почта,
    а не имена пользователей.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Создание пользователя с адресом электронной почты и паролем.
        """
        if not email:
            raise ValueError('Необходимо указать адрес электронной почты.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создание суперпользователя с адресом электронной почты и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        return self.create_user(email, password, **extra_fields)
