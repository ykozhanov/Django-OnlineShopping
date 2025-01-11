from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save, post_delete, post_init
from django.dispatch import receiver, Signal
from django.core.cache import cache
from .models import Category, Product
from .services.category_service import CategoryService

clear_menu_cache_signal = Signal()


@receiver([post_save, post_delete, post_init, clear_menu_cache_signal], sender=Category)
def clear_menu_cache(sender, **kwargs):
    cache.delete(make_template_fragment_key("category-menu"))


@receiver([post_save, post_delete], sender=Product)
def reset_category_cache(sender, instance, created, **kwargs):
    if instance.pk:
        category = instance.category
        cache_key = f"products_in_category_{category.name}"
        cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Category)
def reset_categories(sender, instance, **kwargs):
    CategoryService.categories = None
