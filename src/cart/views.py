import json
from django.db.models import F, Sum
from django.http import JsonResponse
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
    """Refresh products quantity in the cart or delete"""
    
    if request.method == 'POST':
        cart: Cart = get_object_or_404(Cart, user=request.user)
        item: CartItem = get_object_or_404(CartItem, id=item_id, cart=cart)

        if action == 'add':
            item.quantity += 1
            item.save()
        elif action == 'remove' and item.quantity > 1:
            item.quantity -= 1
            item.save()
        elif action == 'set':
            data = json.loads(request.body)
            quantity = data.get('quantity', 1)
            if quantity > 0:
                item.quantity = quantity
                item.save()
        elif action == 'delete':
            item.delete()

        # Refreshing total price
        total_price = cart.items.aggregate(
            total=Sum(F('quantity') * F('product_seller__price'))
        )['total'] or 0

        if action == 'delete':
            return JsonResponse({
                'success': True,
                'total_price': total_price,
                'reload': True,
            })
    
        return JsonResponse({
            'success': True,
            'total_price': total_price,
            'item_quantity': item.quantity if action != 'delete' else 0,
        })
    
    return JsonResponse({'success': False}, status=400)