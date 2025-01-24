from .models import SiteSetting, Category

def menu_cache_timeout_setting(request):
    """Передаёт определённые настройки в шаблон."""
    return {
        'MENU_CACHE_TIMEOUT_SETTING': SiteSetting.get_or_create_default('MENU_CACHE_TIMEOUT_SETTING', 86400),
    }

def category_context_processor(request):
    """Передает категории товаров в шаблон"""
    return {
        "active_category_list": Category.objects.all(),
    }
