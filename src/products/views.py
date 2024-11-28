from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.contrib import messages

from .models import Product
from .forms import ReviewForm


# Create your views here.

class ProductDetailView(DetailView):
    model = Product


def load_reviews(request, pk, offset):
    """
    View for loading a batch of reviews for a product
    """
    count_display = 5
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.filter(is_active=True)[offset:offset+count_display]
    reviews_data = [
        {
            "username": review.user.username,
            "created_at": review.created_at.strftime('%B %d / %Y / %H:%M'),
            "text": review.text
        }
        for review in reviews
    ]
    return JsonResponse(
        {
            "reviews": reviews_data,
            "has_more": product.reviews.filter(is_active=True).count() > offset + count_display
        }
    )

def add_review(request, pk):
    """
    View for add new review (use js)
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=pk)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return JsonResponse({
                'username': review.user.username,
                'created_at': review.created_at.strftime('%B %d / %Y / %H:%M'),
                'text': review.text
            })
        messages.error(request, form.errors)
        return JsonResponse({'errors':form.errors}, status=400)