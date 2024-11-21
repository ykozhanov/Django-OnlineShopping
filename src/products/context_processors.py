from .models import SiteSetting

def menu_cache_timeout_setting(request):
    """Передаёт определённые настройки в шаблон."""
    return {
        'MENU_CACHE_TIMEOUT_SETTING': SiteSetting.get_or_create_default('MENU_CACHE_TIMEOUT_SETTING', 86400),
    }