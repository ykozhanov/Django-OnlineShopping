from django.shortcuts import render
from django.views.generic import DetailView
from .models import OrderModel
from products.models import Category
from profiles.forms import CustomUserEditForm


# Create your views here.

def orderview(request):
    templates = 'orders/order_detail.html'
    # templates = 'profiles/user_detail_edit.htmll'
    category_list = Category.objects.all()
    # context = {
    #     'category_list': category_list,
    # }
    user = request.user

    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, request.FILES, instance=user)
        form.request = request
        if form.is_valid():
            form.save()
            return render(request, templates, context={'form':form, 'user': user})
    else:
        form = CustomUserEditForm(initial={'phone_number': user.phone_number})
    return render(request, templates, context={'form':form, 'user': user})



    # user = request.user
    # print(user)
    # category_list = Category.objects.all()
    # context = {
    #     'category_list': category_list,
    # }
    # return render(request, 'orders/order_detail.html', context)

class OrderView(DetailView):
    model = OrderModel
