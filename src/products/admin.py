from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.urls import path
from django_mptt_admin.admin import DjangoMpttAdmin
from django.utils.html import format_html
from django.shortcuts import render

from .models import Category, Characteristic, Product, ProductCharacteristicValue, SiteSetting, ReviewModel
from .signals import clear_menu_cache_signal
from importapp.forms import JSONImportForm


@admin.action(description='Deactivate entities')
def mark_inactive(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_active=False)


@admin.action(description='Activate entities')
def mark_active(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(is_active=True)


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    """Displaying categories in admin panel"""

    actions = [
        mark_active,
        mark_inactive,
    ]

    list_display = 'pk', 'name', 'parent_name', 'description_short', 'is_active', 'sort_index'
    list_display_links = 'pk', 'name'
    ordering = ('sort_index', 'name')
    search_fields = ('name', 'description')

    def description_short(self, obj: Category) -> str:
        return obj.description if len(obj.description) < 48 else obj.description[:48] + '...'
    
    def parent_name(self, obj: Category) -> str | None:
        return obj.parent.name if obj.parent else None

    fieldsets = [
        (None, {
            'fields': ('name', 'description', 'parent'),
        }),
        ('Icon', {
            'fields': ('icon', ),
        }),
        ('Extra options', {
            'fields': ('is_active', 'sort_index'),
            'classes': ('collapse',),
            'description': 'Extra options'
        })
    ]


class ProductCharacteristicsInline(admin.TabularInline):
    """Inline characteristics of product for vizualization in admin panel"""
    
    model = ProductCharacteristicValue
    extra = 1  # Num of blank lines for filling new characteristics
    autocomplete_fields = ['characteristic']
    fields = 'characteristic', 'value'



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Displaying products in damin panel"""
    change_list_template = "products/products_changelist.html"

    actions = [
        mark_active,
        mark_inactive,
    ]
    inlines = [
        ProductCharacteristicsInline,
    ]
    list_display = 'pk', 'name', 'category_link', 'description_short', 'is_active', 'sort_index'
    list_display_links = 'pk', 'name'
    ordering = ('sort_index', 'name')
    search_fields = ('name', 'description')
    fieldsets = [
        (None, {
            'fields': ('name', 'description', 'category', ),
        }),
        ('Image', {
            'fields': ('image', ),
        }),
        ('Extra options', {
            'fields': ('is_active', 'sort_index', 'limited_edition'),
            'classes': ('collapse',),
            'description': 'Extra options'
        })
    ]

    def category_link(self, obj: Product):
        """Creates link field"""

        #http://127.0.0.1:8000/admin/products/category/3/change/
        if obj.category:
            url = f'/admin/{obj.category._meta.app_label}/{obj.category._meta.model_name}/{obj.category.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return '-'
    
    def description_short(self, obj: Product) -> str:
        """Creates shorrt description"""
        return obj.description if len(obj.description) < 48 else obj.description[:48] + '...'

    def import_json(self, request: HttpRequest) -> HttpResponse:
        form = JSONImportForm()
        context = {
            "form": form,
        }
        return render(request, "admin/json-form.html", context=context)

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-json/",
                self.import_json,
                name="import_products_json",
            ),
        ]
        return new_urls + urls

@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    """Displaying characteristics in admin panel"""

    # inlines = [
    #     CategoriesInline,  # related categories
    # ]
    list_display = 'pk', 'name', 'value_type'
    list_display_links = 'pk', 'name'
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    """Displaying site settings in admin panel"""
    list_display = ('key', 'value')
    search_fields = ('key',)
    change_list_template = "products/settings_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'trigger-clear-menu-cache/',
                self.admin_site.admin_view(self.send_clear_menu_cache_on_category_change),
                name='clear_menu_cache_on_category_change_trigger_signal',
            ),
        ]
        return custom_urls + urls

    def send_clear_menu_cache_on_category_change(self, request):
        clear_menu_cache_signal.send(
            sender=Category,)
        self.message_user(request, message="Category menu cache successfully cleared.",)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))


@admin.register(ReviewModel)
class ReviewAdmin(admin.ModelAdmin):
    """Displaying reviews in damin panel"""
    actions = [mark_active, mark_inactive]
    list_display = ('pk','product', 'user',  'text_short', 'created_at', 'is_active')
    list_display_links = ('pk', 'product')
    search_fields = ('product__name', 'user__username')
    ordering = ('pk', 'product', 'created_at')

    def text_short(self, obj: ReviewModel) -> str:
        """Creates short text"""
        return obj.text if len(obj.text) < 48 else obj.text[:48] + '...'

