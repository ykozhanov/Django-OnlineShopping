from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import DetailView

from .models import Product
from .forms import ReviewForm


# Create your views here.

class ProductDetailView(DetailView):
    model = Product


def add_review(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product-detail', pk=product.id)
        return render(request, 'products/product_detail.html', {'object': product, 'form': form})
    return HttpResponseRedirect(reverse('product-detail', kwargs={'pk': pk}))