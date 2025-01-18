from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.template.defaulttags import url
from django.views.generic import DetailView
from .models import OrderModel
from products.models import Category
from profiles.forms import CustomUserEditForm
from cart.models import Cart, CartItem
from django.urls import reverse
from .forms import OrderStep2Forms, OrderStep3Forms
from django.db.models import Prefetch
from .utils import calculate_total_price

# Create your views here.

def order_step1_view(request):
    templates = 'orders/order_detail.html'
    category_list = Category.objects.all()
    user = request.user

    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, request.FILES, instance=user)
        form.request = request
        if form.is_valid():
            # form.save()
            # context = {
            #     'category_list': category_list,
            #     'form': form, 'user': user
            # }
            return redirect(reverse('orders:orders_step2'))
    else:
        form = CustomUserEditForm(initial={'phone_number': user.phone_number})
    context = {
        'category_list': category_list,
        'form': form, 'user': user
    }
    return render(request, templates, context=context)


def order_step2_view(request):
    """view for check type delivery, city, address and add in session (step 2)"""
    templates = 'orders/order_detail_2.html'
    category_list = Category.objects.all()
    user = request.user

    if request.method == 'POST':
        form = OrderStep2Forms(request.POST)
        if form.is_valid():
            delivery = form.cleaned_data['delivery']
            city = form.cleaned_data['city']
            address = form.cleaned_data['address']
            request.session['order'] = {
                'delivery': delivery,
                'city': city,
                'address': address
            }
            return redirect(reverse('orders:orders_step3'))
    else:
        form = OrderStep2Forms()
    context = {
        'category_list': category_list,
        'user': user,
        'form': form
    }
    return render(request, templates, context=context)


def order_step3_view(request):
    """view for check type pay and add in session (step 3)"""
    templates = 'orders/order_detail_3.html'
    category_list = Category.objects.all()
    user = request.user
    if request.method == 'POST':
        form = OrderStep3Forms(request.POST)
        if form.is_valid():
            order = request.session.get('order', {})
            order['pay'] = form.cleaned_data['pay']
            request.session['order'] = order
            return redirect(reverse('orders:orders_step4'))
    else:
        form = OrderStep3Forms()
    context = {
        'category_list': category_list,
        'user': user,
        'form': form
    }
    return render(request, templates, context=context)


def order_step4_view(request):
    templates = 'orders/order_detail_4.html'
    category_list = Category.objects.all()
    user = request.user
    order = request.session.get('order', {})
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
                'price': item.product_seller.price,
                'quantity': item.quantity,
                'total_price': item.total_price,
                'product_short_description': item.product_seller.product.short_description,
                'image': item.product_seller.product.image,
                'seller': item.product_seller.seller.pk
            })
    total_cost = calculate_total_price(data=cart_data, order=order)
    if request.method == 'POST':
        pass
            #return redirect(reverse('orders:orders_step4'))

    else:
        context = {
            'category_list': category_list,
            'user': user,
            'order': order,
            'cart_data': cart_data,
            'total_cost': total_cost
        }
    return render(request, templates, context=context)
