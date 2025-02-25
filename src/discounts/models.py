from django.db import models

from products.models import Category, Product

DISCOUNT_TYPES = (
    ("percent", "Процент"),
    ("amount", "Сумма"),
    ("fixed", "Фиксированная цена"),
)


class ProductsGroup(models.Model):
    """"Модель групп продуктов для применения скидок"""
    name = models.CharField(max_length=255, verbose_name="Название группы")
    products = models.ManyToManyField(Product, verbose_name="Продукты", related_name="product_groups")

    def __str__(self):
        return self.name


class DiscountBase(models.Model):
    """АБстрактная модель с общей информацией о скидке"""
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание")
    start_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, verbose_name="Тип скидки")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Значение для типа скидки")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Минимальный остаток суммы при скидке на сумму", default=1)
    priority = models.IntegerField(verbose_name="Приоритет")
    is_active = models.BooleanField(verbose_name='Активная ли скидка')

    class Meta:
        abstract = True


class Discount(DiscountBase):
    """Модель скидок на категории и группы продуктов.
    Может быть скидка сразу на несколько категорий, групп продуктов"""

    categories = models.ManyToManyField(Category, related_name='discounts', blank=True,)
    product_groups = models.ManyToManyField(ProductsGroup, related_name="discounts", blank=True)

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

    product_groups = models.ManyToManyField(ProductsGroup, related_name="cart_discounts", blank=True, verbose_name='Группы товаров, для общей скидки на сочетания')

    def __str__(self):
        return self.name
