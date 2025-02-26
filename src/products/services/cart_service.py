from cart.models import Cart, CartItem
from sellers.models import ProductSeller


def get_or_create_user_cart(request):
    """Get or create user cart"""
    user = request.user
    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session=session_key)
    return cart


def change_or_create_cart_item(request):
    """Change or create user cart items"""
    cart = get_or_create_user_cart(request=request)
    data = request.POST
    product_seller_id = data.get('product_seller_id')
    quantity = int(data.get('amount'))
    product_seller = ProductSeller.objects.get(id=product_seller_id)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_seller=product_seller,
        defaults = {'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()