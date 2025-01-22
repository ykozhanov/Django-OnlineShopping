from django.shortcuts import render, redirect
from celery.result import AsyncResult
import random
from .models import OrderModel
from products.models import Category
from profiles.forms import CustomUserEditForm, CustomUserCreationFormForOrder
from cart.models import Cart, CartItem
from django.urls import reverse
from .forms import OrderStep2Forms, OrderStep3Forms, OrderStep4Froms
from django.db.models import Prefetch
from .utils import calculate_total_price
from .tasks import process_payment

# Create your views here.

def order_step1_view(request):
    """"view for check user data and register or login (if not authenticated), then redirect to step2"""
    templates = 'orders/order_detail.html'
    category_list = Category.objects.all()
    user = request.user


    if request.method == 'POST':
        if not user.is_authenticated:
            post_data = request.POST.copy()
            post_data['password1'] = request.POST['password']
            post_data['password2'] = request.POST['password_reply']
            form = CustomUserCreationFormForOrder(post_data)
            if form.is_valid():
                form.save(request=request)
                return redirect(reverse('orders:orders_step2'))
        else:
            return redirect(reverse('orders:orders_step2'))
    else:
        if user.is_authenticated:
            phone_number = user.phone_number
        else:
            phone_number = ''
        form = CustomUserEditForm(initial={'phone_number': phone_number})
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
    """view for check data, save order model and redirect to payment (step 4)"""
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
                'seller': item.product_seller.seller.pk,
                'pk': item.pk
            })
    total_cost = calculate_total_price(data=cart_data, order=order)
    if request.method == 'POST':
        cart_item_pk = [item.get('pk','') for item in cart_data]
        form_data = {
            "delivery": order.get('delivery', ''),
            "city": order.get('city', ''),
            "address": order.get('address', ''),
            "pay": order.get('pay', ''),
            'total_cost': total_cost,

        }
        form = OrderStep4Froms(data=form_data)
        form.is_valid()
        existing_order = OrderModel.objects.filter(
                user=user,
                delivery=form.cleaned_data['delivery'],
                city=form.cleaned_data['city'],
                address=form.cleaned_data['address'],
                pay=form.cleaned_data['pay'],
                total_cost=form.cleaned_data['total_cost']
        ).first()

        if existing_order:
            order = request.session['order']
            order['pk'] = str(existing_order.pk)
            order['total_cost'] = str(existing_order.total_cost)
            request.session['order']= order
            return redirect(reverse('orders:payment'))

        order_instance = form.save(commit=False)
        order_instance.user = user
        order_instance.save()
        order_instance.cart_items.set(cart_item_pk)
        order = request.session['order']
        order['pk'] = str(order_instance.pk)
        order['total_cost'] = str(order_instance.total_cost)
        request.session['order'] = order
        return redirect(reverse('orders:payment'))


    else:
        context = {
            'category_list': category_list,
            'user': user,
            'order': order,
            'cart_data': cart_data,
            'total_cost': total_cost
        }
    return render(request, templates, context=context)


def payment_view(request):
    """view that handles the payment process for an order.
    It retrieves order details from the session, processes a payment form submission, updates the order with the provided card number,
    and initiates an asynchronous payment processing task using Celery.
    After initiating the task, it redirects the user to a payment progress page.
    """
    template = 'orders/payment.html'
    order = request.session.get('order', {})
    pay = order.get('pay',''),
    order_pk = order.get('pk',''),
    total_cost = order.get('total_cost', '')

    if request.method == "POST":
        card_number = request.POST.get('numero1')
        order = OrderModel.objects.get(pk=order.get('pk'))
        order.card_number = card_number
        order.save()
        order = request.session.get('order', '')
        order['card_number'] = card_number
        request.session['order'] = order

        relative_url = "url fakepai"
        api_url = request.build_absolute_uri(relative_url)
        task = process_payment(order_pk=order_pk, card_number=card_number, total_cost=total_cost, api_url=api_url)
        request.session['task_id'] = task

        return redirect(reverse('orders:payment_progress'))
    return render(request, template, context={'pay':pay})


def progress_payment_view(request):
    """
    view that handles the progress of a payment process.
    Check status task and return data to template
    """
    template = 'orders/payment_progress.html'
    task = request.session['task_id']
    task_result = task.get('result')
    if task_result == 'success':
        data = task.get('data')
        # del request.session['order']
        # del request.session['task_id']
        request.session.save()
        return render(request, template, context={'data':data})

    return render(request, template)
