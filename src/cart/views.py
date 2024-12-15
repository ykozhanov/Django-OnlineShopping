from django.db.models import F, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView

from cart.models import Cart, CartItem

class CartView(TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        cart_items = cart.items.select_related('product_seller__product', 'product_seller__seller')
        total_price = cart_items.aggregate(
            total=Sum(F('quantity') * F('product_seller__price'))
        )['total'] or 0

        context.update({
            'cart_items': cart_items,
            'total_price': total_price,
        })
        return context
    
def update_cart_item(request, item_id, action):
    """Refresh products quantity in th cart or delete"""
    
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if action == 'add':
        item.quantity += 1
    elif action == 'remove' and item.quantity > 1:
        item.quantity -= 1
    elif action == 'delete':
        item.delete()
        return redirect('cart/cart.html')
    item.save()
    return redirect('cart/cart.html')
