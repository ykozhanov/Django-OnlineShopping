from django import forms
from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.safestring import mark_safe

from products.models import Category, Product
from .models import Seller, ProductSeller

User = get_user_model()


def has_moderators_groups(user):
    if user.is_superuser:
        return True
    cache_key = f"user_groups_{user.id}"
    groups = cache.get(cache_key)
    if groups is None:
        groups = list(user.groups.values_list('name', flat=True))
        cache.set(cache_key, groups, 60)
    return 'moderators' in groups


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    fields = ['user', 'name', 'phone', 'address', 'description', 'image', 'get_image', 'is_active']
    list_display = ('id', 'name', 'phone', 'address', 'is_active', 'description', 'get_image', 'user')
    ordering = ('id', 'name', 'user', 'is_active')
    list_display_links = ('name', )
    search_fields = ('name', 'user__username')
    readonly_fields = ('get_image', )
    actions = None


    def get_fields(self, request, obj=None):
        """Удаляет поле владелец товара если не moderators"""
        if not has_moderators_groups(request.user):
            if 'user' in self.fields:
                self.fields.remove('user')
        return self.fields


    def has_delete_permission(self, request, obj=None):
        """Удаляет кнопку delete из формы если не moderators"""
        return has_moderators_groups(request.user)


    def has_add_permission(self, request):
        """Позволяет moderators добавлять seller"""
        return has_moderators_groups(request.user)


    def get_actions(self, request):
        """Добавляет delete_selected если moderators"""
        actions = super().get_actions(request)
        if has_moderators_groups(request.user):
            actions['delete_selected'] = (delete_selected, 'delete_selected', 'Удалить выбранные')
        return actions


    def get_queryset(self, request):
        """ Возвращает seller для отображения. У модератора возвращает список всех seller."""
        if has_moderators_groups(request.user):
            return Seller.objects.all()
        else:
            return Seller.objects.filter(user=request.user)


    @admin.display(description='Изображение')
    def get_image(self, seller: Seller):
        """Возвращает изображение seller если оно есть."""
        if seller.image:
            return mark_safe(f'<img src="{seller.image.url}" width="50" height="50">')
        return 'Нет изображения'


class ProductSellerForm(forms.ModelForm):
    """Выбор products по установленной category"""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категория')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = getattr(self, 'current_user', None)
        self.permissions()


    def permissions(self):
        self.get_products_for_category()
        if not has_moderators_groups(self.user):
            self.users_form()


    def users_form(self):
        """убирает отображение поля seller если не moderators"""
        self.fields['seller'].initial = self.user.seller
        self.fields['seller'].widget = forms.HiddenInput()


    def get_products_for_category(self):
        """возвращает products по установленной category при создании формы или ошибке валидации"""
        category_id = self.data.get('category')
        if category_id:
            category = Category.objects.get(id=category_id)
            descendants = category.get_descendants()
            products = Product.objects.filter(
                category_id__in=[category_id] + [d.id for d in descendants])
            self.fields['product'].queryset =products


    class Meta:
        model = ProductSeller
        fields = ('category', 'product', 'seller', 'price')


@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    form = ProductSellerForm
    change_form_template = 'admin/sellers/change_form.html'
    list_display = ['id', 'product', 'product_category', 'price', 'seller', 'product_image']
    list_editable = ('price', )
    list_display_links = None
    search_fields = ('product__name', 'seller__name')
    list_per_page = 20


    def get_list_display(self, request):
        """удаляет поле отображения seller если не moderators"""
        if not has_moderators_groups(request.user):
            if 'seller' in self.list_display:
                self.list_display.remove('seller')
        return self.list_display


    def get_queryset(self, request):
        """Возвращает список моделей product-seller для отображения."""
        if has_moderators_groups(request.user):
            return ProductSeller.objects.all()
        return ProductSeller.objects.filter(seller__user=request.user)


    def get_form(self, request, obj=None, **kwargs):
        """передаёт текущего user в форму добавления товара"""
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form


    @admin.display(description='Изображение')
    def product_image(self, obj):
        """возвращает изображение товара если есть"""
        if obj.product.image:
            return mark_safe(f'<img src="{obj.product.image.url}" width="50" height="50">')
        return 'Нет изображения'


    @admin.display(description='Категория')
    def product_category(self, obj):
        """возвращает категорию для товара"""
        return obj.product.category
