from django.contrib.sessions.models import Session
from django.http import HttpRequest

from sellers.models import ProductSeller
from cart.models import Cart, CartItem

class CartManager:
    """Manager of cart operations"""

    def __init__(self, request: HttpRequest):
        self._cart: Cart = self._get_or_create_cart(request=request)

    @property
    def cart(self) -> Cart:
        """Cart getter"""
        return self._cart

    def _get_or_create_cart(self, request: HttpRequest) -> Cart:
        """Get or create cart by authenticated user or session"""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user, session=None)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key

            session = Session.objects.get(session_key=session_key)
            cart, created = Cart.objects.get_or_create(session=session, user=None)
        return cart
    
    def add_item(self, product: ProductSeller, quantity: int = 1) -> CartItem:
        """Add item to cart. If item already exists in the cart - update quantity"""
        cart_item, created = CartItem.objects.get_or_create(cart=self._cart, product_seller=product)
        if not created:
            return self.update_item_quantity(item=cart_item, increment=quantity)
        else:
            cart_item.quantity = quantity
            cart_item.save()

    def remove_item(self, item: CartItem) -> bool:
        """Remove item of cart"""
        if item in self.get_cart_items():
            item.delete()
            return True
        else:
            # If item is not found in the cart
            return False

    def update_item_quantity(self, item: CartItem, increment: int) -> CartItem | None:
        """Update item quantity"""
        if increment >= 0 or item.quantity + increment > 0:
            item.quantity += increment
            item.save()
            return item
        elif item.quantity + increment <= 0:
            self.remove_item(item=item)
                
    def get_cart_items(self) -> list[CartItem]:
        """Get all cart items"""
        return self._cart.items.select_related('product_seller__product', 'product_seller__seller').all()

    def get_total_items_quantity(self) -> int:
        """Get total items quantity"""
        items_quantity: int = 0
        for item in self._cart.items.all():
            items_quantity += item.quantity
        return items_quantity
    

