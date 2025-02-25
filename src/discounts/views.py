from django.views.generic import ListView
from django.utils import timezone

from products.models import Product
from .models import Discount


class DiscountListView(ListView):
    paginate_by = 12
    model = Product
    template_name = "discounts/discount_list.html"

    @property
    def discounts(self):
        return Discount.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now())

    def get_queryset(self):
        return Product.objects.filter(discounts__in=self.discounts, is_active=True).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_discounts = {}
        for product in context["object_list"]:
            product_discounts[product.pk] = self.discounts.filter(products=product).last()
        context["product_discounts"] = product_discounts
        return context