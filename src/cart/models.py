from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
    

class Cart(models.Model):
    """Cart model"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Related user',
        related_name='cart',
    )
    session_id = models.CharField(
        max_length=255,
        null=True,
        verbose_name='Session id for no-autorized user',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Cart adding datetime',
    )

    def __str__(self):
        if self.user:
            return f'Cart of {self.user.email}'
        else:
            return f'Cart of session {self.session_id}'


from products.models import Product
class FakeProductSeller(models.Model):
    """FAKE! Delete after adding normal model"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Related product',
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Related seller'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Product price',
    )

    def __str__(self):
        return f'{self.seller} - {self.product}'

class CartItem(models.Model):
    """Cart item model"""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        verbose_name='Related cart',
        related_name='items',
    )
    product_seller = models.ForeignKey(
        FakeProductSeller,  # Change after adding normal model 
        on_delete=models.CASCADE,
        verbose_name='Related product of seller',
    )
    quantity = models.IntegerField(
        default=1,
        verbose_name='Products quantity',
    )
    
    class Meta:
        unique_together = ('cart', 'product_seller')

    @property
    def total_price(self):
        return self.product_seller.price * self.quantity


