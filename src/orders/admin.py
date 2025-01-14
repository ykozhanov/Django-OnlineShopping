from django.contrib import admin
from .models import OrderModel

# Register your models here.

@admin.register(OrderModel)
class OrderViews(admin.ModelAdmin):
    list_display = 'pk', 'user', 'delivery', 'city', 'address', 'pay'
