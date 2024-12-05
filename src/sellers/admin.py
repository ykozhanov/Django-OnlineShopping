from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from products.models import Category, Product
from .models import Seller, ProductSeller

User = get_user_model()


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    fields = ('user', 'name', 'phone', 'address', 'description', 'image', 'get_image', 'is_active')
    list_display = ('id', 'name', 'phone', 'address', 'is_active', 'description', 'get_image', 'user')
    ordering = ('id', 'name', 'user', 'is_active')
    list_display_links = ('name', )
    search_fields = ('name', 'user__username')
    readonly_fields = ('get_image', )


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """При создании seller установка текущего пользователя владельцем"""
        if not request.user.has_perm('moderators'):
            if db_field.name == "user":
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def has_add_permission(self, request):
        """Убираем возможность создать seller если он уже создан"""
        if request.user.has_perm('moderators'):
            return True
        return not Seller.objects.filter(user=request.user).exists()


    def get_queryset(self, request):
        """ Возвращает seller для отображения. У модератора возвращает список всех seller."""
        if request.user.has_perm('moderators'):
            return Seller.objects.all()
        else:
            return Seller.objects.filter(user=request.user)


    @admin.display(description='Изображение')
    def get_image(self, seller: Seller):
        """Возвращает изображение seller если оно есть."""
        if seller.image:
            return mark_safe(f'<img src="{seller.image.url}" width="50" height="50">')
        return 'Нет изображения'


    def get_form(self, request, obj=None, **kwargs):
        """Автозаполнение для поля user при создании или редактировании seller текущим пользователем."""
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['user'].initial = request.user
        return form


class ProductSellerForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='Категория'
    )

    def __init__(self, *args, **kwargs):
        """Выбор products по установленной category"""
        super().__init__(*args, **kwargs)
        if self.is_bound and not self.is_valid():
            category_id = self.data.get('category')
            if category_id:
                category = Category.objects.get(id=category_id)
                descendants = category.get_descendants()
                products = Product.objects.filter(category_id__in=[category_id] + [d.id for d in descendants])
                self.fields['product'].queryset = products

    class Meta:
        model = ProductSeller
        fields = ('category', 'product', 'seller', 'price')


@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    form = ProductSellerForm
    change_form_template = 'admin/sellers/change_form.html'
    list_display = ('id', 'product', 'product_category', 'price', 'seller', 'product_image')
    list_editable = ('price', )
    list_display_links = None
    search_fields = ('product__name', 'seller__name')
    list_per_page = 20


    def has_add_permission(self, request):
        """Убираем возможность создать product-seller если нет seller"""
        if request.user.has_perm('moderators'):
            return True
        return Seller.objects.filter(user=request.user).exists()


    def get_queryset(self, request):
        """Возвращает список моделей product-seller для отображения."""
        if request.user.has_perm('moderators'):
            return ProductSeller.objects.all()
        return ProductSeller.objects.filter(seller__user=request.user)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Отсеивает список чужих seller у пользователя если он не модератор"""
        if not request.user.has_perm('moderators'):
            if db_field.name == "seller":
                kwargs["queryset"] = Seller.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    def get_form(self, request, obj=None, **kwargs):
        """При добавлении товара установка seller текущего пользователя если не модератор"""
        form = super().get_form(request, obj, **kwargs)
        if obj is None and not request.user.has_perm('moderators'):
            form.base_fields['seller'].initial = Seller.objects.get(user=request.user)
        return form


    @admin.display(description='Изображение')
    def product_image(self, obj):
        return obj.product.image.url if obj.product.image else "Нет изображения"


    @admin.display(description='Категория')
    def product_category(self, obj):
        return obj.product.category


