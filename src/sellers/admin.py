from typing import Optional

from django import forms
from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.safestring import mark_safe, SafeString

from products.models import Category, Product
from .models import Seller, ProductSeller

User = get_user_model()


def has_moderators_groups(user: User) -> bool:
    return user.is_superuser or user.groups.filter(name="moderators").exists()


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    fields = ["user", "name", "phone", "address", "description", "image", "get_image", "is_active"]
    list_display = ("id", "name", "phone", "address", "is_active", "description", "get_image", "user")
    ordering = ("id", "name", "user", "is_active")
    list_display_links = ("name",)
    search_fields = ("name", "user__username")
    readonly_fields = ("get_image",)
    actions = None

    def get_fields(self, request: HttpRequest, obj=None)-> QuerySet:
        """Удаляет поле владелец товара если не moderators"""
        if not has_moderators_groups(request.user):
            if "user" in self.fields:
                self.fields.remove("user")
        return self.fields

    def has_delete_permission(self, request: HttpRequest, obj=None)-> bool:
        """Удаляет кнопку delete из формы если не moderators"""
        return has_moderators_groups(request.user)

    def has_add_permission(self, request: HttpRequest)-> bool:
        """Позволяет moderators добавлять seller"""
        return has_moderators_groups(request.user)

    def get_actions(self, request: HttpRequest) -> dict:
        """Добавляет delete_selected если moderators"""
        actions = super().get_actions(request)
        if has_moderators_groups(request.user):
            actions["delete_selected"] = (
                delete_selected,
                "delete_selected",
                "Удалить выбранные",
            )
        return actions

    def get_queryset(self, request: HttpRequest)-> QuerySet:
        """Возвращает seller для отображения. У модератора возвращает список всех seller."""
        queryset = super().get_queryset(request)
        if not has_moderators_groups(request.user):
            queryset = queryset.filter(user=request.user)
        return queryset

    @admin.display(description="Изображение")
    def get_image(self, seller: Seller)-> Optional[SafeString]:
        """Возвращает изображение seller если оно есть."""
        if seller.image:
            return mark_safe(f'<img src="{seller.image.url}" width="50" height="50">')


class ProductSellerForm(forms.ModelForm):
    """Выбор products по установленной category"""

    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label="Категория")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = getattr(self, "current_user", None)
        self.get_products_for_category()

    def get_products_for_category(self)-> None:
        """возвращает products по установленной category при создании формы или ошибке валидации"""
        category_id = self.data.get("category")
        if category_id:
            category = Category.objects.get(id=category_id)
            descendants = category.get_descendants()
            products = Product.objects.filter(category_id__in=[category_id] + [d.id for d in descendants])
            self.fields["product"].queryset = products

    class Meta:
        model = ProductSeller
        fields = ("category", "product", "seller", "price", "delivery_type", "payment_type", "quantity")


@admin.register(ProductSeller)
class ProductSellerAdmin(admin.ModelAdmin):
    form = ProductSellerForm
    change_form_template = "admin/sellers/change_form.html"
    list_display = [
        "id",
        "product",
        "quantity",
        "product_category",
        "price",
        "seller",
        "payment_type",
        "delivery_type",
        "product_image",
    ]
    list_editable = ("price",)
    list_display_links = 'id',
    search_fields = ("product__name", "seller__name")
    list_per_page = 20

    def get_list_display(self, request: HttpRequest)-> list:
        """удаляет поле отображения seller если не moderators"""
        list_display = [*self.list_display]
        if not has_moderators_groups(request.user) and "seller" in list_display:
            list_display.remove("seller")
        return list_display

    def get_queryset(self, request: HttpRequest)-> QuerySet:
        """Возвращает список моделей product-seller для отображения."""
        if has_moderators_groups(request.user):
            return ProductSeller.objects.all()
        return ProductSeller.objects.filter(seller__user=request.user)

    def get_form(self, request: HttpRequest, obj=None, **kwargs)-> ProductSellerForm:
        """передаёт текущего user в форму добавления товара"""
        form = super().get_form(request, obj, **kwargs)
        if not has_moderators_groups(request.user):
            form.base_fields["seller"].initial = request.user.seller
            form.base_fields["seller"].widget = forms.HiddenInput()
        return form

    @admin.display(description="Изображение")
    def product_image(self, obj: ProductSeller) -> SafeString:
        """возвращает изображение товара если есть"""
        if obj.product.image:
            return mark_safe(f'<img src="{obj.product.image.url}" width="50" height="50">')

    @admin.display(description="Категория")
    def product_category(self, obj: ProductSeller) -> SafeString:
        """возвращает категорию для товара"""
        return obj.product.category
