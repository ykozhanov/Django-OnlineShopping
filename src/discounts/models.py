from django.db import models

from products.models import Category, Product

DISCOUNT_TYPES = (
    ("percent", "Процент"),
    ("fixed", "Фиксированная скидка"),
)


class DiscountBase(models.Model):
    __abstract__ = True

    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание")
    start_date = models.DateTimeField(verbose_name="Дата начала")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания")
    type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, verbose_name="Тип скидки")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Значение для типа скидки")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Минимальный остаток")
    priority = models.IntegerField(verbose_name="Приоритет")


class Discount(DiscountBase):
    """Модель скидок на категории и группы продуктов"""

    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.CASCADE, related_name="category_discounts"
    )
    products = models.ManyToManyField(Product, related_name="discounts", blank=True)


class ProductsGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название группы")
    products = models.ManyToManyField(Product, verbose_name="Продукты", related_name="products_group")

    def __str__(self):
        return self.name


class CartDiscount(DiscountBase):
    """Модель скидок на корзину"""

    min_items = models.IntegerField(null=True, blank=True, verbose_name="min товаров")
    max_items = models.IntegerField(null=True, blank=True, verbose_name="max товаров")
    min_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Минимальная сумма"
    )
    max_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Максимальная сумма"
    )

    products_group = models.ManyToManyField(ProductsGroup, related_name="cart_discounts")

    def __str__(self):
        return self.name
