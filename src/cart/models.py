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
        
