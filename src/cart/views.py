import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from cart.cart_manager import CartManager
from cart.models import Cart, CartItem

class CartView(TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_manager: CartManager = CartManager(request=self.request)
        cart_items: list[CartItem] = cart_manager.get_cart_items()

        context.update({
            'cart_items': cart_items,
        })
        return context
    
def update_cart_item(request, item_id, action):
    """Refresh products quantity in the cart or delete view"""
    
    if request.method == 'POST':
        cart_manager: CartManager = CartManager(request=request)
        cart: Cart = cart_manager.cart
        item: CartItem = get_object_or_404(CartItem, id=item_id, cart=cart)

        reload_page: bool = False
        updated_cart_item = None
        if action in ['add', 'remove']:
            increment: int = 1 if action == 'add' else -1
            updated_cart_item: CartItem | None = cart_manager.update_item_quantity(
                item=item,
                increment=increment,
            )
            if not updated_cart_item:
                reload_page = True
        elif action == 'set':
            data = json.loads(request.body)
            quantity = data.get('quantity', 1)
            updated_cart_item: CartItem | None = cart_manager.set_item_quantity(
                item=item,
                quantity=quantity,
            )
            if not updated_cart_item:
                reload_page = True
        elif action == 'delete':
            cart_manager.remove_item(item=item)
            reload_page = True
        else:
            raise ValueError('Operation value is not correct')

        total_price: float = cart_manager.get_total_items_price()
        total_quantity: int = cart_manager.get_total_items_quantity()
        item_quantity: int = updated_cart_item.quantity if updated_cart_item else 0
    
        return JsonResponse({
            'success': True,
            'total_price': total_price,
            'total_quantity': total_quantity,
            'item_quantity': item_quantity,
            'reload': reload_page,
        })
    
    return JsonResponse({'success': False}, status=400)
