from django.core.management import BaseCommand
from django.db import transaction

from products.models import Category

class Command(BaseCommand):
    """
    Creates categories
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating categories...')

        categories: list[dict] = [
            {'name': 'Home', 'description': 'Products for home', 'parent_name': None},
            {'name': 'Clothes', 'description': 'Clothes for men and women', 'parent_name': None},
            {'name': 'Kitchen', 'description': 'Products for kitchen', 'parent_name': 'Home'},
        ]

        created_categories: dict[str, Category] = {}
        for category in categories:
            parent_name: str = category.pop('parent_name')
            parent = created_categories.get(parent_name) if parent_name else None

            category_obj, created = Category.objects.get_or_create(
                name=category.get('name'),
                defaults={
                    'description': category.get('description'),
                    'parent': parent,
                }
            )

            created_categories[category_obj.name] = category_obj

            self.stdout.write(f'Created category {category_obj.name}')

        self.stdout.write(self.style.SUCCESS('Categories created!'))

