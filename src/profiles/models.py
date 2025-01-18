import os

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from .managers import CustomUserManager

def user_image_directory_path(instance: 'User', filename: str):
    """Generates a file path for uploading user images"""
    file_extension: str = filename.split('.')[-1]
    return 'users/{id}.{extension}'.format(
        id=instance.id,
        extension=file_extension,
    )

def validate_image_size(value):
    """Validates that the file size does not exceed the specified maximum size in kilobytes"""
    max_size_kb = 2 * 1024
    if value.size > max_size_kb * 1024:
        raise ValidationError(f'Max file size is {max_size_kb}sKB')


class User(AbstractUser):
    phone_number_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must be 10 digits.")
    email = models.EmailField('email address', unique=True)
    is_seller = models.BooleanField(default=False)
    phone_number = models.CharField(validators=[phone_number_regex],max_length=10,blank= True, null=True)
    avatar = models.ImageField(blank=True, null=True, validators=[validate_image_size])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Save method redefinition to firstly get user id and then get path to icon"""
        is_new: bool = self.id is None
        if not is_new:
            old_avatar = User.objects.filter(pk=self.pk).first().avatar
            if old_avatar and self.avatar != old_avatar:
                if old_avatar.path and os.path.exists(old_avatar.path):
                    os.remove(old_avatar.path)
        super().save(*args, **kwargs)
        if is_new and self.avatar:
            new_avatar_path: str = user_image_directory_path(self, self.avatar.name)
            self.avatar.storage.save(new_avatar_path, self.avatar.file)
            self.avatar.name = new_avatar_path
            super().save(update_fields=['avatar'])
