from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html


from .models import Cart, CartItem
from .models import FakeProductSeller


User = get_user_model()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Displaying carts in admin panel"""

    list_display = 'pk', 'get_user_email', 'session_id', 'created_at'
    search_fields = 'user__email', 'session_id'
    list_filter = ('created_at', )

    fieldsets = [
        (None, {
            'fields': ('user', 'session_id', 'created_at'),
        })
    ]
    readonly_fields = ('created_at', )

    def get_user_email(delf, obj):
        """Get user email if user is related"""
        if obj.user:
            url = f'/admin/{obj.user._meta.app_label}/{obj.user._meta.model_name}/{obj.user.pk}/'
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'
    
    get_user_email.short_description = 'User Email'  # field name id admin panel
    get_user_email.allow_tags = True  # allows to dicplay refs


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Displaying cart items in admin panel"""

    list_display = 'pk', 'get_cart_ref', 'get_product_seller_ref', 'quantity'
    ordering = ('pk',)
    # search_fields = 'user__email', 'price'

    # fieldsets = [
    #     (None, {
    #         'fields': ('user', 'session_id', 'created_at'),
    #     })
    # ]
    def get_cart_ref(self, obj):
        """Get related cart ref"""
        url = f'/admin/{obj.cart._meta.app_label}/{obj.cart._meta.model_name}/{obj.cart.pk}/'
        return format_html('<a href="{}">{}</a>', url, obj.cart)
    
    def get_product_seller_ref(self, obj):
        """Get related product_seller ref"""
        url = f'/admin/{obj.product_seller._meta.app_label}/{obj.product_seller._meta.model_name}/{obj.product_seller.pk}/'
        return format_html('<a href="{}">{}</a>', url, obj.product_seller)

    get_cart_ref.short_description = 'Cart'
    get_product_seller_ref.short_description = 'Product of seller'

@admin.register(FakeProductSeller)
class FakeProductSellerAdmin(admin.ModelAdmin):
    """FAKEFAKEFAKE"""

    list_display = 'pk', 'get_product_ref', 'get_seller_ref', 'price'
    ordering = ('pk', )
    # search_fields = 'user__email', 'price'

    # fieldsets = [
    #     (None, {
    #         'fields': ('user', 'session_id', 'created_at'),
    #     })
    # ]
    def get_product_ref(self, obj):
        """Get related product ref"""
        url = f'/admin/{obj.product._meta.app_label}/{obj.product._meta.model_name}/{obj.product.pk}/'
        return format_html('<a href="{}">{}</a>', url, obj.product)
    
    def get_seller_ref(self, obj):
        """Get related seller ref"""
        url = f'/admin/{obj.seller._meta.app_label}/{obj.seller._meta.model_name}/{obj.seller.pk}/'
        return format_html('<a href="{}">{}</a>', url, obj.seller)

    get_product_ref.short_description = 'Product'
    get_seller_ref.short_description = 'Seller'
