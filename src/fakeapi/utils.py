import random

def fake_payment_service(card_number):
    """
    Simulates a payment service by validating a card number and returning a payment result
    """
    card_number = card_number.replace(' ','')
    if int(card_number) % 2 == 0 and not card_number.endswith('0'):
        return {'status': 'success', 'message': 'Оплата подтверждена'}
    else:
        errors = [
            'Недостаточно средств',
            'Карта заблокирована',
            'Ошибка сети',
            'Неверный номер карты',
        ]
        return {'status': 'error', 'message': random.choice(errors)}