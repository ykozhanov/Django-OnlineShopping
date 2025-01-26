from cart.models import Cart, CartItem
from django.db.models import Prefetch
from .models import DeliveryPriceModel
from .tasks import process_payment


def get_cart_data(user):
    cart = Cart.objects.filter(user=user).prefetch_related(
        Prefetch(
            'items',
            queryset=CartItem.objects.select_related('product_seller__product')
        )
    ).first()
    cart_data = []
    if cart:
        for item in cart.items.all():
            cart_data.append({
                'product_name': item.product_seller.product.name,
                'price': float(item.product_seller.price),
                'quantity': item.quantity,
                'total_price': float(item.total_price),
                'product_short_description': item.product_seller.product.short_description,
                'image': item.product_seller.product.image.url,
                'seller': item.product_seller.seller.pk,
                'pk': item.pk
            })
    return cart_data


from .models import DeliveryPriceModel

def delivery_type_price():
    """Return cost of delivery from BD"""
    deliveries_type = DeliveryPriceModel.objects.all()
    cost_express = 0
    cost_ordinary = 0
    total_price_order = 0

    for delivery_type in deliveries_type:
        if delivery_type.delivery == 'ordinary':
            cost_ordinary = delivery_type.price
            total_price_order = delivery_type.total_price_order
        else:
            cost_express = delivery_type.price
    return cost_ordinary, total_price_order, cost_express



def calculate_total_price(data: list, order: dict)->float:
    """ Returns the total order cost including the delivery cost """
    cost_ordinary,total_price_order, cost_express  = delivery_type_price()
    total_cost = 0
    sellers = set()
    for item in data:
        total_cost += item.get('total_price', 0)
        sellers.add(item.get('seller', 0))
    if order['delivery'] == 'express':
        total_cost += cost_express
    elif total_cost < total_price_order or len(sellers) > 1:
        total_cost += cost_ordinary
    return float(total_cost)



class ServiceForPayment:
    """
    Fake class for add order in payment and get payment
    Будет скорректирован в дальнейшем
    """
    api_url = "url fakepai"

    def __init__(self, order_pk, card_number, total_cost):
        self.api_url = "url fakepai"
        self.order_pk = order_pk
        self.card_number =card_number
        self.total_cost = total_cost
        self.payment = {}

    def add_payment(self):
        """Будет скорректирован в рамках 6 спринта"""
        self.payment = process_payment(
            order_pk=self.order_pk,
            card_number=self.card_number,
            total_cost=self.total_cost,
            api_url=self.api_url
        )
        return self.payment

    def get_payment_status(self):
        """Будет реализован в рамках 6 спринта"""
        self.payment = process_payment(
            order_pk=self.order_pk,
            card_number=self.card_number,
            total_cost=self.total_cost,
            api_url=self.api_url
        )
        return self.payment