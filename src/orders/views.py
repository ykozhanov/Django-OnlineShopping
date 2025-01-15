from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.template.defaulttags import url
from django.views.generic import DetailView
from .models import OrderModel
from products.models import Category
from profiles.forms import CustomUserEditForm
from django.urls import reverse
from .forms import OrderStep2Forms, OrderStep3Forms


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
    templates = 'orders/order_detail_2.html'
    category_list = Category.objects.all()
    user = request.user

    if request.method == 'POST':
        form = OrderStep2Forms(request.POST)
        # print(form.data, 'form_data')
        if form.is_valid():
            # print('form_valid')
            return redirect(reverse('orders:orders_step3'))

        # print(form.errors)
    else:
        form = OrderStep2Forms()
    context = {
        'category_list': category_list,
        'user': user,
        'form': form
    }
    return render(request, templates, context=context)


def order_step3_view(request):
    templates = 'orders/order_detail_3.html'
    category_list = Category.objects.all()
    user = request.user

    if request.method == 'POST':
        form = OrderStep3Forms(request.POST)
        print(form.data, 'form_data')
        if form.is_valid():
            print('form_valid')
            return redirect(reverse('orders:orders_step4'))

        print(form.errors)
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

    if request.method == 'POST':
        form = OrderStep3Forms(request.POST)
        print(form.data, 'form_data')
        if form.is_valid():
            print('form_valid')
            # return redirect(reverse('orders:orders_step4'))

        print(form.errors)
    else:
        form = OrderStep3Forms()
    context = {
        'category_list': category_list,
        'user': user,
        'form': form
    }
    return render(request, templates, context=context)




def orderviewstep1(request):
    print('step1')

    user = request.user
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, request.FILES, instance=user)
        form.request = request
        if form.is_valid():
            print(form.data)
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)





class OrderView(DetailView):
    model = OrderModel
