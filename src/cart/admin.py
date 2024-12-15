from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html


from .models import Cart


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