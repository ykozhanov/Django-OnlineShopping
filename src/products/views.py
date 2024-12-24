from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.views import generic

from .models import Product
from .forms import ReviewForm

# Create your views here.


def load_reviews(request, pk, offset):
    """
    View for loading a batch of reviews for a product
    """
    count_display = 5
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.filter(is_active=True).order_by("-created_at")[offset : offset + count_display]
    review_count = product.reviews.filter(is_active=True).count()
    reviews_data = [
        {
            "username": review.user.username,
            "created_at": review.created_at.strftime("%B %d / %Y / %H:%M"),
            "text": review.text,
        }
        for review in reviews
    ]
    return JsonResponse(
        {
            "reviews": reviews_data,
            "has_more": product.reviews.filter(is_active=True).count() > offset + count_display,
            "review_count": review_count,
        }
    )


def add_review(request, pk):
    """
    View for add new review (use js)
    """
    if request.method == "POST":
        product = get_object_or_404(Product, id=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            review_count = product.reviews.filter(is_active=True).count()
            return JsonResponse(
                {
                    "username": review.user.username,
                    "created_at": review.created_at.strftime("%B %d / %Y / %H:%M"),
                    "text": review.text,
                    "review_count": review_count,
                }
            )
        messages.error(request, form.errors)
        return JsonResponse({"errors": form.errors}, status=400)


class SellerDetailView(generic.DetailView):
    """блок «Продавцы» на детальной странице товара"""

    model = Product
    template_name = "products/seller_detail_on_product_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sellers = self.object.sellers.all().select_related("seller")
        sellers_data = []
        for seller in sellers:
            seller_data = {
                "name": seller.seller.name,
                "price": seller.price,
                "delivery_type": seller.get_delivery_type_display(),
                "payment_type": seller.get_payment_type_display(),
            }
            sellers_data.append(seller_data)
        context["sellers_data"] = sellers_data
        return context
