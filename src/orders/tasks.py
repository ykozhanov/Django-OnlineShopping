from celery import shared_task
import requests
from django.urls import reverse

@shared_task
def process_payment(order_pk, card_number, total_cost, api_url):
    """
    This task sends a request to an external API to process a payment and returns the result
    of the operation
    """

    payload = {
        'card_number': card_number,
        'order_id': order_pk,
        'total_cost': total_cost,
    }
    response = requests.post(api_url, data=payload)
    result = response.json()
    if response.status_code == 200:
        return {'result': 'success', 'data':result}

    return {'result': 'not success'}