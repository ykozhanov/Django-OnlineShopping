from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


class ComparisonList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name="comparisons")

    def __str__(self):
        return f"Comparison list for {self.user.email}"
