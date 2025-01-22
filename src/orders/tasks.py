import requests

def process_payment(order_pk, card_number, total_cost, api_url):
    """
    Это функция заглушка, будет полностью реализована в рамках 6 спринта  6 задачи
    This task sends a request to an external API to process a payment and returns the result
    of the operation
    """

    payload = {
        'card_number': card_number,
        'order_id': order_pk,
        'total_cost': total_cost,
    }
    result = 200
    if result == 200:
        return {'result': 'success', 'data':payload}

    return {'result': 'not success'}