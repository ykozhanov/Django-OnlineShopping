from django.core.management import BaseCommand
from django.db import transaction

from sellers.models import Seller


class Command(BaseCommand):
    """Создание seller"""

    @transaction.atomic
    def handle(self, *args, **options)-> None:
        self.stdout.write("Create seller")

        sellers_data = [
            {
                "name": "Пятёрочка",
                "description": "Описание Пятёрочка",
                "image": "пятёрочка.jpg",
                "phone": "+7 555 901-23-45",
                "address": "Адрес Пятёрочка",
                "email": "пятёрочка@5.ru",
                "is_active": True,
                "user_id": 1,
            },
            {
                "name": "Дикси",
                "description": "Описание Дикси",
                "image": "дикси.jpg",
                "phone": "+7 999 901-23-99",
                "address": "Адрес Дикси",
                "email": "дикси@dic.ru",
                "is_active": True,
                "user_id": 2,
            },
            {
                "name": "Магнит",
                "description": "Описание Магнит",
                "image": "магнит.jpg",
                "phone": "+7 777 333-23-33",
                "address": "Адрес Магнит",
                "email": "mag@mag.ru",
                "is_active": True,
                "user_id": 3,
            },
            {
                "name": "x5",
                "description": "Описание X5",
                "image": "x5.jpg",
                "phone": "+7 050 050-05-05",
                "address": "Адрес X5",
                "email": "x5@x5.ru",
                "is_active": True,
                "user_id": 4,
            },
        ]
        for seller_data in sellers_data:
            seller, created = Seller.objects.get_or_create(
                name=seller_data["name"],
                defaults=seller_data,
            )
            self.stdout.write(f"Created seller {seller.name}")

        self.stdout.write(self.style.SUCCESS("Sellers created"))
