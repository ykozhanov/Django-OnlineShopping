from django.http import HttpRequest

from .cart_manager import CartManager


def main_header_cart_data(request: HttpRequest) -> dict:
    """Data for cart-block of main header"""
    cart_manager: CartManager = CartManager(request=request)
    total_products_count: int = cart_manager.get_total_items_quantity()
    total_products_price: float = cart_manager.get_total_items_price()
    return {
        'total_products_count': total_products_count,
        'total_products_price': total_products_price,
    }