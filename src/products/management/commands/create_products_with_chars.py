from django.core.management import BaseCommand
from django.db import transaction

from products.models import Category, Characteristic, Product, ProductCharacteristicValue

class Command(BaseCommand):
    """
    Creates products with characteristics
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

        self.stdout.write('Creating products...')
        products: list[dict] = [
            {'name': 'T-shirt', 'category_name': 'Clothes', 'description': 'Very beautiful t-shirt'},
            {'name': 'Pot', 'category_name': 'Kitchen', 'description': 'Very qualitative pot'},
        ]

        created_products: dict[str, Product] = {}
        for product in products:
            product_obj, created = Product.objects.get_or_create(
                name=product.get('name'),
                defaults={
                    'description': product.get('description'),
                    'category': created_categories.get(product.get('category_name')),
                }
            )
            created_products[product_obj.name] = product_obj
            self.stdout.write(f'Created product {product_obj.name}')

        self.stdout.write('Creating characteristics...')
        characteristics: list[dict] = [
            {'name': 'Weight, kg', 'value_type': 'float',},
            {'name': 'Color', 'value_type': 'string'},
        ]

        created_characteristics: dict[str, Characteristic] = {}
        for characteristic in characteristics:
            characteristic_obj, created = Characteristic.objects.get_or_create(
                name=characteristic.get('name'),
                defaults={
                    'value_type': characteristic.get('value_type'),
                }
            )
            created_characteristics[characteristic_obj.name] = characteristic_obj
            self.stdout.write(f'Created characteristic {characteristic_obj.name}')

        self.stdout.write('Creating connections...')
        characteristic_values: list[dict] = [
            {
                'product_name': 'T-shirt', 'characteristics': [
                    {'name': 'Weight, kg', 'value': '0.125'},
                    {'name': 'Color', 'value': 'White'},
                ]
            },
            {
                'product_name': 'Pot', 'characteristics': [
                    {'name': 'Weight, kg', 'value': '0.550'},
                    {'name': 'Color', 'value': 'Grey'},
                ]
            }
        ]

        created_product_chars: list[ProductCharacteristicValue] = []
        for product in characteristic_values:
            product_obj = created_products.get(product.get('product_name'))
            for characteristic in product.get('characteristics'):
                characteristic_obj = created_characteristics.get(characteristic.get('name'))
                product_characteristic, created = ProductCharacteristicValue.objects.get_or_create(
                    product=product_obj,
                    characteristic=characteristic_obj,
                    value=characteristic.get('value'),
                )
                created_product_chars.append(product_characteristic)
                self.stdout.write(f'Created connection between {product_obj.name} and {characteristic_obj.name} with value {product_characteristic.value}')
        
        self.stdout.write(self.style.SUCCESS('Products, Characteristics and their connections created!'))

