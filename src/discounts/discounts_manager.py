from datetime import datetime

from django.db.models import Q, Sum, F

from cart.models import CartItem
from discounts.models import Discount, DiscountBase, CartDiscount
from products.models import Product, Category
from sellers.models import ProductSeller


class DiscountsManager:
    """Класс с функционалом расчета скидок"""
    
    def get_all_products_discounts(self, products: list[Product]) -> dict[Product, dict[str, list[Discount | int]]]:
        """"Возвращает словарь продуктов со связанными скидками"""
        if not products:
            return {}
        discounts_dict: dict[Product, dict[str, list[Discount | int]]] = {}
        products_with_discounts = Product.objects.filter(
            id__in=[product.id for product in products],
        ).prefetch_related(
            'product_groups__discounts'  # получаем скидки на группы продуктов, в которые входит продукт
        ).prefetch_related(
            'product_groups__cart_discounts'  # получаем скидки на группы продуктов, входящих в набор для скидки
        ).prefetch_related(
            'category__parent'  # получаем связанные категории и родительские категории для дальнейшего извлечения скидок по ним
        )

        category_ids: set[int] = set()
        for product in products_with_discounts:
            discounts_dict[product] = {'group_discount': [], 'category_ids': [], 'category_discounts': []}

            # получаем id категорий
            discounts_dict[product]['category_ids'].append(product.category.id)  # добавляем id прямой категории товвара
            parent = product.category.parent
            while parent:  # проходимся по родительским категориям
                discounts_dict[product]['category_ids'].append(parent.id)
                parent = parent.parent
            
            # добавляем id категорий в общий набор
            category_ids.update(discounts_dict[product]['category_ids'])

            # заполняем групповые скидки
            for group in product.product_groups:
                if group.discounts:
                    discounts_dict[product]['group_discount'].extend(group.discounts)
            
        # Запрашиваем категории со связями на скидки
        categories = Category.objects.filter(id__in=category_ids).prefetch_related('discounts')
        discounts_by_category = {}
        for category in categories:
            discounts_by_category[category.id] = category.discounts

        # Заполянем скидки на категории
        for product, data in products_with_discounts.items():
            for category_id in data['category_ids']:
                discounts = discounts_by_category.get(category_id)
                if discounts:
                    data['category_discounts'].extend(discounts)
        return products_with_discounts


    def get_priority_products_discounts(self, products: list[Product]) -> dict[Product, list[Discount]]:
        """"Возвращает словарь продуктов с приоритетными скидками (может быть несколько скидок с одинаковым приоритетом)"""
        prorduct_discounts: dict[Product, dict] = self.get_all_products_discounts(products=products)
        res: dict[Product, list[Discount]] = {}
        for product, data in prorduct_discounts.items():
            if not data.get('group_discount') and not data.get('category_discounts'): # у товара нет скидок
                res[product] = []
                continue

            discounts: list[Discount] = data.get('group_discount').extend(data.get('category_discounts'))  # все имеющиеся скидки
            active_discounts: list[Discount] = []
            for discount in discounts:
                if not discount.is_active:  # не включаем деактивированную
                    continue
                if discount.end_date < datetime.now():  # не включаем с истекшим сроком скидки
                    continue
                if discount.start_date and discount.start_date > datetime.now():  # не включаем с ненаступившим сроком скидки
                    continue
                active_discounts.append(discount)

            if not active_discounts:
                res[product] = []
                continue

            max_priority_value: int = max([discount.priority for discount in active_discounts])
            priority_discounts: list[Discount] = [discount for discount in active_discounts if discount.priority == max_priority_value]
            res[product] = priority_discounts
        return res
    
    
    def calculate_products_prices(self, products_prices: dict[Product, float | None]) -> dict[Product, float]:
        """Возвращает словарь продуктов и расчитанных цен с учетом скидок
        Если не передана фиксированная цена товара - берется максимальная по продавцам"""
        products_discounts: dict[Product, list[Discount]] = self.get_priority_products_discounts(
            products=list(products_prices.keys())
        )
        discount_prices: dict[Product, float] = {}
        for product, discounts in products_discounts.items():
            price: float | None = products_prices.get(product)
            if not price:
                # Берется максимальная цена по продавцам товара
                product_sallers: list[ProductSeller] = ProductSeller.objects.filter(product=product)
                price: float = max([product_saller.price for product_saller in product_sallers])

            if not discounts:
                discount_prices[product] = price
                continue

            discount_price: float = price
            for discount in discounts:
                discount_price = min(discount_price, self._calc_discount_price(price=price, discount=discount))
            discount_prices[product] = discount_price
        return discount_prices


    def _calc_discount_price(self, price: float, discount: DiscountBase) -> float:
        """Возвращает цену после применения скидки"""
        if discount.type == 'percent':
            discount_price: float = price * (1 - discount.value / 100)
        elif discount.type == 'amount':
            discount_price = max(discount.min_amount, price - discount.value)  # цена не станет ниже рубля
        elif discount.type == 'fixed':
            discount_price = min(price, discount.value)  # цена не станет ниже начальной цены
        else:
            discount_price = price
        return round(discount_price, 2)
    
    def calculate_cart_discount_price(
            self,
            cart_items: list[CartItem],
            total_price: float = None,
            total_count: float = None,
        ):
        """Возвращает цену на корзину с учетом применения скидки"""
        if not total_price:
            total_price = CartItem.objects.filter(
                id__in=[item.id for item in cart_items]
            ).aggregate(
                total=Sum(F('quantity') * F('product_seller__price'))
            )['total'] or 0

        if not total_count:
            total_count = CartItem.objects.filter(
                id__in=[item.id for item in cart_items]
            ).aggregate(
                total=Sum(F('quantity'))
            )['total'] or 0

        active_cart_discounts: list[CartDiscount] = list(CartDiscount.objects.filter(
            Q(is_active=True) &
            Q(end_date__gte=datetime.now()) &
            (Q(start_date__isnull=True) | Q(start_date__lte=datetime.now()))
        ).prefetch_related('product_groups__products'))

        if not active_cart_discounts:
            return total_price
        
        # словарь скидок, которые можно применить для корзины и прайс корзины после применения
        available_discounts: dict[CartDiscount, float] = {} 

        for discount in active_cart_discounts:
            discount_value: float | None = self._calc_cart_discount_price(
                cart_items=cart_items,
                total_price=total_price,
                total_count=total_count,
                discount=discount,
            )
            if discount_value:
                available_discounts[discount] = discount_value

        if not available_discounts:
            return total_price

        max_priority: int = max([discount.priority for discount in available_discounts.keys()])
        priority_discounts: dict[Discount, float] = {
            discount: price
            for discount, price in available_discounts.items()
            if discount.priority == max_priority
            }
        return min(total_price, min(priority_discounts.values()))
    
    def _calc_cart_discount_price(
            self,
            cart_items: list[CartItem],
            total_price: float,
            total_count: int,
            discount: CartDiscount,
        ) -> float | None:
        """Возвращает цену корзины со скидкой если скидка применима, иначе None"""
        if not discount.product_groups:  # Расчет по параметрам корзины
            if discount.min_items and total_count < discount.min_items:
                return None
            if discount.max_items and total_count > discount.max_items:
                return None
            if discount.min_total and total_price < discount.min_total:
                return None
            if discount.max_total and total_price > discount.max_total:
                return None
            return self._calc_discount_price(
                price=total_price,
                discount=discount,
            )

        else:  # Расчет по наборам
            if not discount.product_groups:
                return None
            # проверка наличия в корзине товаров из каждой группы для применения скидки
            cart_products: dict[Product, dict[str, float | int | bool]] = {
                cart_item.product_seller.product: {
                    'quantity': cart_item.quantity,
                    'price': cart_item.product_seller.price,
                    'is_included_in_set': False,
                }
                for cart_item in cart_items
            }
            products_count_to_discount: int = len(discount.product_groups)  # кол-во различных товаров, необходимое для применения скидки
            for group in discount.product_groups:
                for product in cart_products:
                    if product in group.products:
                        cart_products[product]['is_included_in_set'] = True
                        discount.product_groups -= 1
                        break  # в корзине есть товар из группы
            if products_count_to_discount > 0:
                return None  # скидка не применяется
            
            discount_products_quantity: int = min(
                product_details.get('quantity')
                for product_details in cart_products.values()
                if product_details.get('is_included_in_set')
            )  # кол-во товаров для скидки за набор (общий максимум)

            total_price: float = 0
            total_price += sum(
                product_detail.get('quantity') * product_detail.get('price')
                for product_detail in cart_products.values()
                if product_detail.get('is_included_in_set') == False
            )  # добавление товаров без скидки набора
            total_price += self._calc_discount_price(
                price=sum(
                    product_details.get('price')
                    for product_details in cart_products.values()
                    if product_details.get('is_included_in_set')
                )
            ) * discount_products_quantity  # добавление товаров со скидкой набора (с учетом максимального совеместного кол-ва)
            total_price += sum(
                product_details.get('price') * (product_details.get('quantity') - discount_products_quantity)
                for product_details in cart_products.values()
                if product_details.get('is_included_in_set')
            )
            return total_price
