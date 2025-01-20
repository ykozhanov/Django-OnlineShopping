from django.contrib import admin
from .models import OrderModel, DeliveryPriceModel

# Register your models here.

@admin.register(OrderModel)
class OrderViews(admin.ModelAdmin):
    list_display = 'pk', 'user', 'delivery', 'city', 'address', 'pay', 'created_at', 'status'
    list_display_links = 'pk', 'user'

@admin.register(DeliveryPriceModel)
class DeliveryPriceModel(admin.ModelAdmin):
    list_display = 'pk', 'delivery', 'price'
    list_display_links = 'pk', 'delivery'