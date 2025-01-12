from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import DetailView
from django.core.cache import cache

from .models import Product, SiteSetting, ReviewModel
from .forms import ReviewForm
from sellers.models import ProductSeller


def get_cache_key(product_id):
    return f'product_detail_{product_id}'


# Create your views here.
def load_reviews(request, pk, offset):
    """
    View for loading a batch of reviews for a product
    """
    count_display = 5
    product = get_object_or_404(Product, id=pk)
    reviews = product.reviews.filter(is_active=True).order_by("-created_at")[offset:offset+count_display]
    review_count = product.reviews.filter(is_active=True).count()
    reviews_data = [
        {
        "username": review.user.username,
        "created_at": review.created_at.strftime('%B %d / %Y / %H:%M'),
        "text": review.text,
        'first_name': review.user.first_name,
        'last_name': review.user.last_name,
        } for review in reviews
    ]
    return JsonResponse(
        {
            "reviews": reviews_data,
            "has_more": product.reviews.filter(is_active=True).count() > offset + count_display,
            'review_count': review_count
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
            review_count = product.reviews.filter(is_active=True).count()
            return JsonResponse(
                {
                    'created_at': review.created_at.strftime('%B %d / %Y / %H:%M'),
                    'text': review.text,
                    'review_count': review_count,
                    'first_name': review.user.first_name,
                    'last_name': review.user.last_name,
                }
            )
        messages.error(request, form.errors)
        return JsonResponse({'errors':form.errors}, status=400)


class ProductDetailView(DetailView):
    """
    View for display the product detail info
    """
    model = Product
    template_name = 'products/product_detail.html'

    def get_cache_timeout(self):
        """
        Recieve cache timeout from SiteSettings
        """
        timeout = SiteSetting.get_or_create_default('product_cache_timeout', default='2')
        return int(timeout)


    def dispatch(self, *args, **kwargs):
        """
        Check cache key and render page
        """
        cache_key = get_cache_key(self.kwargs.get('pk'))
        timeout = self.get_cache_timeout()
        cache_data = cache.get(cache_key)
        if cache_data:
            return cache_data
        response = super().dispatch(*args, **kwargs)
        if hasattr(response, 'render') and callable(response.render):
            response.render()
        cache.set(cache_key, response, timeout)
        return response


    def get_context_data(self, **kwargs):
        """
        Add product seller id and price with min values
        """
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        sellers = product.sellers.all()
        if sellers:
            min_price_seller = min(sellers, key=lambda seller: seller.price)
            context['min_price_seller_id'] = min_price_seller.id
            context['min_price_seller_price'] = min_price_seller.price

        return context


class AddProductInCart(View):
    """
    Класс заглушка для добавления товара в корзину (нужно будет изменить после создания модели корзины)
    """
    def post(self, request):
        username = request.user
        data = request.POST
        product_seller_id = data.get('product_seller_id')
        amount = data.get('amount')
        print(f'User {username} add in cart product_seller with id={product_seller_id} amount={amount}')
        return JsonResponse({'success': 'Product added to cart successfully'})


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidate_cache_product_model(sender, instance, **kwargs):
    """
    Delete cache if Product have been changed
    """
    product_id = instance.id
    cache_key = get_cache_key(product_id)
    cache.delete(cache_key)


@receiver(post_save, sender=ProductSeller)
@receiver(post_delete, sender=ProductSeller)
def invalidate_cache_product_seller_model(sender, instance, **kwargs):
    """
    Delete cache if  ProductSeller have been changed
    """
    product_id = instance.product.id
    cache_key = get_cache_key(product_id)
    cache.delete(cache_key)


@receiver(post_save, sender=ReviewModel)
@receiver(post_delete, sender=ReviewModel)
def invalidate_cache_review_model(sender, instance, **kwargs):
    """
    Delete cache if ReviewModel have been changed
    """
    product_id = instance.product.id
    cache_key = get_cache_key(product_id)
    cache.delete(cache_key)