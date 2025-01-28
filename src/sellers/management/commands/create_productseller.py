from django.core.management.base import BaseCommand
from django.db import transaction
from random import randint

from products.models import Product
from sellers.models import Seller, ProductSeller


class Command(BaseCommand):
    help = "Create ProductSeller records for each seller"

    def handle(self, *args, **options)-> None:
        with transaction.atomic():
            sellers = Seller.objects.all()
            products = Product.objects.all()

            for seller in sellers:
                for product in products:
                    if not ProductSeller.objects.filter(product=product, seller=seller).exists():
                        ProductSeller.objects.create(
                            product=product,
                            seller=seller,
                            price=randint(1, 1000),
                            delivery_type="STANDARD",
                            payment_type="CARD",
                        )

        self.stdout.write(self.style.SUCCESS("ProductSeller records created successfully"))
