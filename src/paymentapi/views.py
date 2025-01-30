from django.http import JsonResponse
from rest_framework.decorators import api_view
from .services import fake_payment_service

# Create your views here.

@api_view(['POST', 'GET'])
def fake_api_payment(request):
    """
    API endpoint to simulate a payment processing service
    """
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        card_number = request.POST.get('card_number')
        total_cost = request.POST.get('total_cost')
        result = fake_payment_service(card_number)
        return JsonResponse(
            {
                "order_id": order_id,
                "card_number": card_number,
                "total_cost": total_cost,
                'status_pay': result.get('status',''),
                'message': result.get('message')
            }
        )
    return JsonResponse({'status': 'error', 'message': 'Неверный метод запроса'})
