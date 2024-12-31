from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


class ComparisonList(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name="comparisons")

    def add_product(self, product):
        if product not in self.products.all():
            self.products.add(product)

    def remove_product(self, product):
        if product in self.products.all():
            self.products.remove(product)

    def get_products(self, limit=3):
        return self.products.all()[:limit]

    def count_products(self):
        return self.products.count()
