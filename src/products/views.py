from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import DetailView

from .models import Product
from .forms import ReviewForm


# Create your views here.

class ProductDetailView(DetailView):
    model = Product


# def add_review(request, pk):
#     product = get_object_or_404(Product, id=pk)
#     if request.method == 'POST':
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             review = form.save(commit=False)
#             review.product = product
#             review.user = request.user
#             review.save()
#             return redirect('product-detail', pk=product.id)
#         return render(request, 'products/product_detail.html', {'object': product, 'form': form})
#     return HttpResponseRedirect(reverse('product-detail', kwargs={'pk': pk}))

def add_review(request, pk):
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
        print(form.is_valid())


def load_reviews(request, pk, offset):
    count_display = 5
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.filter(is_active=True)[offset:offset+count_display]
    reviews_data = [
        {
            "username": review.user.username,
            "created_at": review.created_at.strftime('%B %d / %Y / %H:%M'),
            "text": review.text
        }
                    for review in reviews]
    return JsonResponse(
        {
            "reviews": reviews_data,
            "has_more": product.reviews.filter(is_active=True).count() > offset + count_display
        }
    )
