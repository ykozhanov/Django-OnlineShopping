from django.db import models

from profiles.models import User
from products.models import Product


class Seller(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sellers', verbose_name='Владелец')
    name = models.CharField(max_length=255, verbose_name='Магазин')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='sellers/', blank=True, null=True, verbose_name='Изображение')
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
        verbose_name = 'Товар в магазине'
        verbose_name_plural = 'Товары в магазинах'

    def __str__(self):
        return f"{self.product.name} - {self.seller.name} (${self.price})"
