from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver

from .models import Cart, CartItem


@receiver(user_logged_in)
def merge_carts(sender, request, user, **kwargs):
    """Carts sinchronization during authorization"""
    session_key = request.session.session_key
    if not session_key:
        # Do nothing if doesnt have session
        return
    
    session_cart = Cart.objects.filter(session__session_key=session_key, user=None).first()
    user_cart = Cart.objects.filter(user=user).first()

    if session_cart and user_cart:
        # Union products
        for item in session_cart.items.all():
            existing_item = user_cart.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = user_cart
                item.save()
        session_cart.delete()

    elif session_cart:
        session_cart.user = user
        session_cart.session = None
        session_cart.save()
        
    

