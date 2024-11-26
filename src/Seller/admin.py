from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.cache import cache
from django.utils.safestring import mark_safe

from .models import Seller, ProductSeller, User, Product


@admin.register(User)
class UserAdmin(UserAdmin):
    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]

    list_display = ('username', 'is_staff',  'get_groups')
    list_display_links = ('username',)


def user_has_permission(user, group_name) -> bool:
    """Проверяет, принадлежит ли пользователь к указанной группе. с кэшированием."""
    if user.is_superuser:
        return True
    cache_key = f"user_{user.id}_group_{group_name}"
    has_group = cache.get(cache_key)
    if has_group is None:
        has_group = user.groups.filter(name=group_name).exists()
        cache.set(cache_key, has_group, timeout=60)
    return has_group

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    fields = ('user', 'name', 'email', 'phone', 'address', 'description', 'image', 'get_image', 'is_active')
    list_display = ('id', 'name', 'email', 'phone', 'address', 'is_active', 'description', 'get_image', 'user')
    list_display_links = ('name', )
    search_fields = ('name', 'user__username')
    readonly_fields = ('get_image', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Настраивает выбор пользователя для поля user при создании или редактировании seller."""
        if not user_has_permission(request.user, 'moderators'):
            if db_field.name == "user":
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """
        Возвращает sellers для отображения.
        Если у пользователя есть разрешение "moderators", он видит всех sellers; иначе — только своих.
        """
        if user_has_permission(request.user, 'moderators'):
            return Seller.objects.all()
        else:
            return Seller.objects.filter(user=request.user)

    @admin.display(description='Изображение')
    def get_image(self, seller: Seller):
        """Возвращает иконку seller если она есть."""
        if seller.image:
            return mark_safe(f'<img src="{seller.image.url}" width="50" height="50">')
        return 'Нет изображения'

    def get_form(self, request, obj=None, **kwargs):
        """Автозаполнение для поля user при создании или редактировании seller текущим пользователем."""
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
        """Фильтрует набор данных на основе выбранного статуса."""
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
        """Настраивает выбор seller с использованием кэширования."""
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'seller':
            choices = getattr(request, '_seller_choices_cache', None)
            if choices is None:
                choices = list(formfield.choices)
                request._seller_choices_cache = choices
            formfield.choices = choices
        return formfield

    def has_add_permission(self, request):
        """Запрет на добавление product при отсутствии seller у пользователя."""
        if not hasattr(request.user, '_sellers_exist'):
            request.user._sellers_exist = request.user.sellers.exists()
        return request.user._sellers_exist

    def get_queryset(self, request):
        """Возвращает список моделей product-seller для отображения."""
        if user_has_permission(request.user, 'moderators'):
            return ProductSeller.objects.all()
        queryset = ProductSeller.objects.filter(seller__user=request.user)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Для текущего пользователя возвращает список доступных product и список доступных seller."""
        if not user_has_permission(request.user, 'moderators'):
            if db_field.name == "seller":
                kwargs["queryset"] = Seller.objects.filter(user=request.user)
            if db_field.name == "product":
                sellers = Seller.objects.filter(user=request.user)
                kwargs["queryset"] = Product.objects.filter(sellers__seller__in=sellers).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
