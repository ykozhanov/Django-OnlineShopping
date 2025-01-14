from django.shortcuts import render
from django.views.generic import DetailView
from .models import OrderModel
from products.models import Category


# Create your views here.

def orderview(request):
    category_list = Category.objects.all()
    print(category_list)
    context = {
        'category_list': category_list,
    }
    return render(request, 'orders/order_detail.html', context)

class OrderView(DetailView):
    model = OrderModel
