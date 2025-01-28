from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from cart.models import CartItem
from django.db.models import Q

User = get_user_model()

# Create your models here.

class OrderModel(models.Model):
    """Order model"""
    DELIVERY_TYPE = [
        ('ordinary', 'Ordinary'),
        ('express', 'Express')
    ]
    PAYMENT_TYPE = [
        ('online', 'Online cart'),
        ('someone', "Online from a random stranger's account.")
    ]
    STATUS_TYPE = [
        ('success', 'Success'),
        ('not success', 'Not success')
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    delivery = models.CharField(
        max_length=10,
        choices=DELIVERY_TYPE,
        default='usually'
    )
    city = models.CharField(
        max_length=30,
        blank=True
    )
    address = models.TextField(
        max_length=200
    )
    pay = models.CharField(
        max_length=100,
        choices=PAYMENT_TYPE,
        default='online'
    )
    cart_items = models.ManyToManyField(
        CartItem,
        related_name='orders'
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Total cost of the order'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_TYPE,
        default='not success',
        blank=True
    )
    card_number = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        verbose_name='card number'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания заказа'
    )
    error_message = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Payment error message',
    )


    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         existing_orders = OrderModel.objects.filter(
    #             user=self.user,
    #             delivery=self.delivery,
    #             city=self.city,
    #             address=self.address,
    #             total_cost=self.total_cost
    #         )
    #         if existing_orders.exists():
    #             raise ValidationError("Заказ с такими данными уже существует.")
    #
    #     super().save(*args, **kwargs)


class DeliveryPriceModel(models.Model):
    """Model for price delivery"""

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(delivery__in=['ordinary', 'express']),
                name='delivery_type_check'
            )
        ]

    DELIVERY_TYPE = [
        ('ordinary', 'Ordinary'),
        ('express', 'Express')
    ]
    delivery = models.CharField(
        max_length=10,
        choices=DELIVERY_TYPE,
        default='usually',
        unique=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='The Сost of the delivery'
    )
    total_price_order = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Total price for order'
    )

    def save(self, *args, **kwargs):
        if self.delivery != 'ordinary':
            self.total_price_order = None
        super().save(*args, **kwargs)
