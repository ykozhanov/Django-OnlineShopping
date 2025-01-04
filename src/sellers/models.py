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
    PAYMENT_CHOICES = [("CARD", "Онлайн картой"), ("CASH", "Наличными")]
    DELIVERY_CHOICES = [
        ("STANDARD", "Обычная доставка"),
        ("EXPRESS", "Быстрая доставка"),
        ("FREE", "Бесплатная доставка"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sellers", verbose_name="Товар")
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="products", verbose_name="Продавец")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    delivery_type = models.CharField(
        max_length=10, choices=DELIVERY_CHOICES, verbose_name="Тип доставки", default="STANDARD"
    )
    payment_type = models.CharField(max_length=50, choices=PAYMENT_CHOICES, verbose_name="Тип оплаты", default="CARD")
    quantity = models.IntegerField(verbose_name="Количество товара", default=0)

    class Meta:
        unique_together = ("product", "seller")
        verbose_name = "Товар продавца"
        verbose_name_plural = "Товары продавца"
