from django.contrib.sessions.models import Session
from django.db.models import F, Sum
from django.http import HttpRequest

from sellers.models import ProductSeller
from cart.models import Cart, CartItem
from products.models import Product

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
    
    def get_product_seller_with_min_price(self, product: Product) -> ProductSeller:
        """Get product of specific seller with min price"""
        product_sellers = ProductSeller.objects.filter(product=product).all()
        if product_sellers:
            product_seller = min(list(product_sellers), key=lambda x: x.price)
            return product_seller
        return None

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

    def set_item_quantity(self, item: CartItem, quantity: int) -> CartItem | None:
        """Set quantity value"""
        if quantity == 0:
            self.remove_item(item=item)
        elif quantity > 0:
            item.quantity = quantity
            item.save()
            return item
        else:
            return item
                
    def get_cart_items(self) -> list[CartItem]:
        """Get all cart items"""
        return self._cart.items.select_related('product_seller__product', 'product_seller__seller').all()

    def get_total_items_quantity(self) -> int:
        """Get total items quantity"""
        
        total_quantity = self._cart.items.aggregate(
                    total=Sum(F('quantity'))
                )['total'] or 0
        return total_quantity

    def get_total_items_price(self) -> float:
        """Get total items price"""
        # TODO: Учесть скидки!
        # total_price: float = self._cart.items

        # items_total_price: float = 0
        # for item in self.get_cart_items():
        #     items_total_price += item.product_seller.price * item.quantity
        # return items_total_price

        total_price = self._cart.items.aggregate(
                    total=Sum(F('quantity') * F('product_seller__price'))
                )['total'] or 0
        return total_price