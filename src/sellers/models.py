from django.contrib.auth import get_user_model
from django.db import models

from products.models import Product

User = get_user_model()


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller", verbose_name="Владелец")
    name = models.CharField(max_length=255, verbose_name="Продавец")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to="sellers/", blank=True, null=True, verbose_name="Изображение")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    email = models.EmailField(verbose_name="Email")
    is_active = models.BooleanField(default=True, verbose_name="Статус активности")

    class Meta:
        verbose_name = "Продавец"
        verbose_name_plural = "Продавец"

    def __str__(self):
        return self.name


class ProductSeller(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sellers", verbose_name="Товар")
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="products", verbose_name="Продавец")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    class Meta:
        unique_together = ("product", "seller")
        verbose_name = "Товар продавца"
        verbose_name_plural = "Товары продавца"

    def __str__(self):
        return f"{self.product.name} - {self.seller.name} (${self.price})"
