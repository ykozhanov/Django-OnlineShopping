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
    return total_cost