from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from .models import Seller, ProductSeller, User, Product


# @admin.register(User)
# class UserAdmin(UserAdmin):
#     def get_groups(self, obj):
#         return [group.name for group in obj.groups.all()]
#
#     list_display = ('username', 'is_staff',  'get_groups')
#     list_display_links = ('username',)


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    fields = ('user', 'name', 'email', 'phone', 'address', 'description', 'image', 'get_image', 'is_active')
    list_display = ('id', 'name', 'email', 'phone', 'address', 'is_active', 'description', 'get_image', 'user')
    list_display_links = ('name', )
    search_fields = ('name', 'user__username')
    readonly_fields = ('get_image', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.groups.filter(name='moderators').exists():
            if db_field.name == "user":
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.groups.filter(name='moderators').exists():
            return Seller.objects.all()
        else:
            return Seller.objects.filter(user=request.user)

    @admin.display(description='Изображение')
    def get_image(self, seller: Seller):
        if seller.image:
            return mark_safe(f'<img src="{seller.image.url}" width="50" height="50">')
        return 'Нет изображения'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['user'].initial = request.user
        return form


class ActiveSellerFilter(admin.SimpleListFilter):
    title = 'Статус магазинов'
    parameter_name = 'active'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Только активные'),
            ('inactive', 'Только неактивные'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(seller__is_active=True)
        elif self.value() == 'inactive':
            return queryset.filter(seller__is_active=False)
        return queryset

@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'price', 'seller')
    list_editable = ('price', 'seller')
    list_display_links = None
    search_fields = ('product__name', 'seller__name')
    list_per_page = 20
    list_filter = (ActiveSellerFilter,)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'seller':
            choices = getattr(request, '_seller_choices_cache', None)
            if choices is None:
                choices = list(formfield.choices)
                request._seller_choices_cache = choices
            formfield.choices = choices
        return formfield

    def has_add_permission(self, request):
        if not hasattr(request.user, '_sellers_exist'):
            request.user._sellers_exist = request.user.sellers.exists()
        return request.user._sellers_exist

    def get_queryset(self, request):
        if request.user.groups.filter(name='moderators').exists():
            return ProductSeller.objects.all()
        queryset = ProductSeller.objects.filter(seller__user=request.user)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.groups.filter(name='moderators').exists():
            if db_field.name == "seller":
                kwargs["queryset"] = Seller.objects.filter(user=request.user)
            if db_field.name == "product":
                sellers = Seller.objects.filter(user=request.user)
                kwargs["queryset"] = Product.objects.filter(sellers__seller__in=sellers).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
