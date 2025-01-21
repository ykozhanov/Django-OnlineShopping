from django.shortcuts import render, redirect
from products.models import Category
from django.urls import reverse

# Create your views here.

def order_step1_view(request):
    """"view for check user data and register or login (if not authenticated), then redirect to step2"""
    templates = 'orders/order_detail.html'
    category_list = Category.objects.all()
    user = request.user
    context = {
        'category_list': category_list,'user': user
    }
    return render(request, templates, context=context)
