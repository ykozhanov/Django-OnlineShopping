from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save, post_delete, post_init
from django.dispatch import receiver, Signal
from django.core.cache import cache
from .models import Category


clear_menu_cache_signal = Signal()

@receiver([post_save, post_delete, post_init, clear_menu_cache_signal], sender=Category)
def clear_menu_cache(sender, **kwargs):
    cache.delete(make_template_fragment_key('category-menu'))