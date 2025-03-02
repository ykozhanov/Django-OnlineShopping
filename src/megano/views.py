from datetime import datetime
from django.db.models import Count, Prefetch
from django.views.generic import TemplateView

from banners.models import Banner
from discounts.discounts_manager import DiscountsManager
from products.models import Category, Product
from products.services.day_offer_service import DayOfferService


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Блок с банерами
        banners = Banner.objects.filter(is_active=True).order_by('?')[:3]
        
        # Блок с топ-категориями
        categories = Category.objects.filter(
            is_active=True
        ).annotate(
            num_products=Count('products')  # Добавляем аннотацию с количеством продуктов
        ).filter(
            num_products__gt=0  # Фильтруем категории, у которых есть хотя бы один продукт
        ).prefetch_related(
            Prefetch('products', queryset=Product.objects.filter(is_active=True))  # Подгружаем только активные продукты
        ).prefetch_related(
            'products__sellers'  # Подгружаем продавцов для продуктов
        ).order_by(
            'sort_index'
        )[:3]  # Берем первые три категории

        # categories = Category.objects.filter(
        #     is_active=True
        # ).prefetch_related(
        #     'products'
        # ).prefetch_related(
        #     'products__sellers'
        # ).order_by(
        #     'sort_index'
        # )[:3]
        top_categories = []
        for category in categories:
            product_prices = []
            for product in category.products.all():
                product_prices.extend([product_seller.price for product_seller in product.sellers.all()])
            min_price = min(product_prices) if product_prices else None
            top_categories.append({'obj': category, 'min_price': min_price})
        
        # Блок с предложением дня
        day_offer: dict = DayOfferService.get_random_product()
        day_offer_product = day_offer.get('day_offer_product')
        if day_offer_product:
            day_offer_product_price = min(seller.price for seller in day_offer_product.sellers.all())
            products_discounts = DiscountsManager().calculate_products_prices(
                {day_offer_product: day_offer_product_price}
            )
            day_offer_product_discount_price = products_discounts.get(day_offer_product)
            if day_offer_product_discount_price >= day_offer_product_price:
                day_offer_product_discount_price = None
        else:
            day_offer_product_price = None
            day_offer_product_discount_price = None

        finished_at: datetime = day_offer.get('finished_at') if day_offer else None
        finished_at_str = finished_at.strftime('%d.%m.%Y %H:%M:%S') if finished_at else None
        
        # Блок с популярными товарами
        top_products = Product.objects.filter(is_active=True).select_related('category').order_by('sort_index')[:8]
        if top_products:
            top_products_with_discount_prices = DiscountsManager().calculate_products_prices(
                products_prices={product: None for product in top_products}
            )
            top_products_with_discount_prices = [{'obj': key, 'price': value} for key, value in top_products_with_discount_prices.items()]
        else:
            top_products_with_discount_prices = []

        # Блок товаров с ограниченным тиражом
        limit_edition_products = Product.objects.filter(is_active=True)
        if day_offer.get('day_offer_product'):
            limit_edition_products = limit_edition_products.exclude(id=day_offer.get('day_offer_product').id)
        limit_edition_products = limit_edition_products.order_by('?')[:8]
        limit_edition_products_with_discount_price = DiscountsManager().calculate_products_prices(
            products_prices={product: None for product in limit_edition_products}
        )
        limit_edition_products_with_discount_price = [{'obj': key, 'price': value} for key, value in limit_edition_products_with_discount_price.items()]

        
        context.update(
            {
                'banners': banners,
                'top_categories': top_categories,
                'day_offer_product': day_offer_product,
                'day_offer_product_price': day_offer_product_price,
                'day_offer_product_discount_price': day_offer_product_discount_price,
                'finished_at': finished_at_str,
                'top_products': top_products_with_discount_prices,
                'limit_edition_products': limit_edition_products_with_discount_price,
            }
        )
        return context


