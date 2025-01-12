from django.db import models

from products.models import Category, Product

DISCOUNT_TYPES = (
    ("percent", "Процент скидки"),
    ("fixed", "Фиксированная скидка"),
)


class Discount(models.Model):
    """Модель скидок на категории и группы продуктов"""

    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название скидки")
    description = models.TextField(verbose_name="Описание скидки")
    start_date = models.DateTimeField(verbose_name="Дата начала скидки")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания скидки")
    type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, verbose_name="Тип скидки")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Значение скидки")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Минимальный остаток")
    priority = models.IntegerField(verbose_name="Приоритет скидки")

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE, related_name="category_discounts"
    )
    products = models.ManyToManyField(Product, related_name="discounts", blank=True)


class CartDiscount(models.Model):
    """Модель скидок на корзину"""

    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название скидки")
    description = models.TextField(verbose_name="Описание скидки")
    start_date = models.DateTimeField(verbose_name="Дата начала скидки")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания скидки")
    type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, verbose_name="Тип скидки")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Значение скидки")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Минимальный остаток")
    min_items = models.IntegerField(null=True, blank=True, verbose_name="Минимальное количество товаров")
    max_items = models.IntegerField(null=True, blank=True, verbose_name="Максимальное количество товаров")
    min_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Минимальная сумма"
    )
    max_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Максимальная сумма"
    )
    discount_priority = models.IntegerField(verbose_name="Приоритет скидки")


class ProductGroup(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_groups")


class DiscountGroup(models.Model):
    product_group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name="discount_groups")
    cart_discount = models.ForeignKey(CartDiscount, on_delete=models.CASCADE, related_name="cart_groups")
