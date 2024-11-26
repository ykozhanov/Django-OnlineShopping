from django.contrib.auth.models import AbstractUser, Group
from django.db import models


# AUTH_USER_MODEL = 'Seller.User'

# class User(AbstractUser):
#     username = models.CharField(max_length=255, unique=True)
#     is_staff = models.BooleanField(default=True)
#
#     def save(self, *args, **kwargs):
#         if not self.pk:
#             group = Group.objects.get(name='users')
#             self.groups.add(group)
#         super().save(*args, **kwargs)
#
# class Product(models.Model):
#     name = models.CharField(max_length=255, verbose_name='Название товара')
#
#     def __str__(self):
#         return self.name

class Seller(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sellers', verbose_name='Владелец')
    name = models.CharField(max_length=255, verbose_name='Магазин')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='sellers/', blank=True, null=True, verbose_name='Иконка')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    email = models.EmailField(verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Статус активности')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return self.name

class ProductSeller(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sellers', verbose_name='Товар')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products', verbose_name='Магазин')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    class Meta:
        unique_together = ('product', 'seller')
        verbose_name = 'Продукт в магазине'
        verbose_name_plural = 'Продукты в магазинах'

    def __str__(self):
        return f"{self.product.name} - {self.seller.name} (${self.price})"
