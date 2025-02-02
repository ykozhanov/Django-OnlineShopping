import random

def fake_payment_service(card_number):
    """
    Simulates a payment service by validating a card number and returning a payment result.
    If the card number is even and does not end with 0, the payment is confirmed.
    If the card number is odd and ends with 0, the service generates a random payment error.
    """
    card_number = card_number.replace(' ','')
    if int(card_number) % 2 == 0 and not card_number.endswith('0'):
        return {'status': 'success', 'message': 'Оплата подтверждена'}
    else:
        errors = [
            'Недостаточно средств',
            'Карта заблокирована',
            'Неверный номер карты',
        ]
        return {'status': 'not success', 'message': random.choice(errors)}