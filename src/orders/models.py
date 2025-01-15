from django.db import models
from django.contrib.auth import get_user_model
from cart.models import CartItem

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
        default='not success'
    )
