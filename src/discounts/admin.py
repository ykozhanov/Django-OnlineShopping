from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.safestring import mark_safe

from discounts.models import Discount, ProductsGroup, CartDiscount


def render_objects_widget(objects):
    widget = FilteredSelectMultiple(is_stacked=False, verbose_name="widget")
    widget.choices = [(obj.pk, obj.name) for obj in objects]
    objects_count = len(objects)
    if objects_count == 1:
        return objects[0].name
    if objects_count > 0:
        html = widget.render(
            "products_group",
            objects,
            attrs={"style": f"width: 20em; height: {objects_count * 16 + 16}px; min-height: 0px; max-height: 160px;"},
        )
        return mark_safe(html)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = (
        "id",
        "name",
        "products_list",
        "category",
        "description",
        "start_date",
        "end_date",
        "type",
        "value",
        "min_amount",
        "priority",
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "products":
            kwargs["widget"] = FilteredSelectMultiple(db_field.verbose_name, False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    @admin.display(description="Товары")
    def products_list(self, obj):
        products = obj.products.all()
        return render_objects_widget(products)


@admin.register(ProductsGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = ("id", "name")

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "products":
            kwargs["widget"] = FilteredSelectMultiple(db_field.verbose_name, False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(CartDiscount)
class CartDiscountAdmin(admin.ModelAdmin):
    list_display_links = ("name",)
    list_display = (
        "id",
        "name",
        "get_products_group",
        "description",
        "start_date",
        "end_date",
        "type",
        "value",
        "min_amount",
        "min_items",
        "max_items",
        "min_total",
        "max_total",
        "discount_priority",
    )

    # get_products_group.short_description = "Группы продуктов"
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "products_group":
            kwargs["widget"] = FilteredSelectMultiple(db_field.verbose_name, False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    @admin.display(description="Группы продуктов")
    def get_products_group(self, obj):
        groups = obj.products_group.all()
        return render_objects_widget(groups)
