from django.utils import timezone
from .models import ViewHistory

class ViewHistoryService:
    def __init__(self, user):
        self.user = user

    def add_to_view_history(self, product):
        """Добавить товар к списку просмотренных товаров"""
        existing_view = ViewHistory.objects.filter(user=self.user, product=product).first()
        if existing_view:
            existing_view.viewed_at = timezone.now()
            existing_view.save()
        else:
            ViewHistory.objects.create(user=self.user, product=product)

    def remove_from_view_history(self, product):
        """Удалить товар из списка просмотренных товаров"""
        ViewHistory.objects.filter(user=self.user, product=product).delete()

    def is_in_view_history(self, product):
        """Узнать, есть ли товар уже в списке просмотренных"""
        return ViewHistory.objects.filter(user=self.user, product=product).exists()

    def get_view_history(self, limit=20):
        """Получить список просмотренных товаров"""
        return ViewHistory.objects.filter(user=self.user).order_by('-viewed_at')[:limit]

    def get_view_history_count(self):
        """Получить количество просмотренных товаров"""
        return ViewHistory.objects.filter(user=self.user).count()