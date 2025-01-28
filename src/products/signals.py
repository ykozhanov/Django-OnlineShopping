from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save, post_delete, post_init
from django.dispatch import receiver, Signal
from django.core.cache import cache
from .models import Category, Product, ReviewModel
from .services.category_service import CategoryService
from sellers.models import ProductSeller

clear_menu_cache_signal = Signal()

def get_cache_key(product_id):
    return f'product_detail_{product_id}'

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


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidate_cache_product_model(sender, instance, **kwargs):
    """
    Delete cache if Product have been changed
    """
    product_id = instance.id
    cache_key = get_cache_key(product_id)
    cache.delete(cache_key)

@receiver(post_save, sender=ProductSeller)
@receiver(post_delete, sender=ProductSeller)
def invalidate_cache_product_seller_model(sender, instance, **kwargs):
    """
    Delete cache if  ProductSeller have been changed
    """
    product_id = instance.product.id
    cache_key = get_cache_key(product_id)
    cache.delete(cache_key)

@receiver(post_save, sender=ReviewModel)
@receiver(post_delete, sender=ReviewModel)
def invalidate_cache_review_model(sender, instance, **kwargs):
    """
    Delete cache if ReviewModel have been changed
    """
    product_id = instance.product.id
    cache_key = get_cache_key(product_id)
    cache.delete(cache_key)