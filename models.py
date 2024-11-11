from django.contrib.auth.models import User
from django.db import models



# Модель категорий каталога
class Category(models.Model):
    """
    # Создание корневой категории
    root_category = Category.objects.create(name='Корневая категория')

    # Создание дочерней категории
    child_category = Category.objects.create(name='Дочерняя категория', parent=root_category)

    # Создание внучатой категории
    grandchild_category = Category.objects.create(name='Внучатая категория', parent=child_category)

    """
    name = models.CharField(max_length=255, verbose_name='Название категории')
    description = models.TextField(verbose_name='Описание категории')
    icon = models.ImageField(upload_to='category_icons', blank=True, null=True, verbose_name='Иконка категории')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', verbose_name='Родительская категория')
    is_active = models.BooleanField(default=True, verbose_name='Статус активности')

    class Meta:
        ordering = ['name']

# Модель баннеров
class Banner(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название баннера')
    image = models.ImageField(upload_to='banners/', verbose_name='Изображение баннера')
    is_active = models.BooleanField(default=True, verbose_name='Статус активности')
    link = models.URLField(verbose_name='Ссылка по которой переходит при нажатии на баннер')

# Модель пользователей
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Модель пользователя')
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Аватарка пользователя', blank=True, null=True)

# Модель продавцов
class Seller(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название "продавца"')
    description = models.TextField(verbose_name='Описание "продавца"')
    image = models.ImageField(upload_to='sellers/', verbose_name='Изображение продавца')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=255, verbose_name='Адрес')
    email = models.EmailField(verbose_name='Email')


# Модель товаров и цен
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена товара')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', verbose_name='Ключ на категорию товара', null=True)
    is_active = models.BooleanField(default=True, verbose_name='Статус доступности товара')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение товара')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления товара')
    limited_edition = models.BooleanField(default=False, verbose_name='Ограниченный тираж')
    sort_index = models.IntegerField(default=0, verbose_name='Индекс сортировки')

    class Meta:
        ordering = ['sort_index', 'price', 'name']

# Модель one-to-many Product - характеристики товара
class ProductCharacteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics', verbose_name='Ключ на продукт')
    name = models.CharField(max_length=255, verbose_name='Название характеристики')
    value = models.CharField(max_length=255, verbose_name='Значение характеристики')

# Модель many-to-many Product - Seller с количеством продаж
class ProductSeller(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sellers', verbose_name='Ключ на продукт')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products', verbose_name='Ключ на продавца')
    sales_count = models.IntegerField(default=0, verbose_name='Количество продаж')

    class Meta:
        ordering = ['-sales_count', 'seller']
        unique_together = ('product', 'seller')

# Модель предложения дня
class DailyOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар предложения дня')
    date = models.DateField(verbose_name='Дата предложения', unique=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('product', 'date')

# Модель корзины
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Ключ на пользователя')

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name='Ключ на корзину')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Ключ на товар')
    quantity = models.IntegerField(default=1, verbose_name='Количество товаров')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Ключ на продавца')

    class Meta:
       unique_together = ('cart', 'product', 'seller')

# Модель способов оплаты
class PaymentMethod(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название способа оплаты')
    description = models.TextField(verbose_name='Описание способа оплаты')

# Модель способов доставки
class DeliveryMethod(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название способа доставки')
    description = models.TextField(verbose_name='Описание способа доставки')
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Стоимость доставки')

ORDER_STATUS_CHOICES = [
    ('created', 'Создан'),
    ('paid', 'Оплачен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
]

# Модель заказов
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Ключ на пользователя')
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.CASCADE, verbose_name='Способ доставки')
    delivery_town = models.CharField(max_length=255, verbose_name='Город доставки')
    delivery_address = models.CharField(max_length=255, verbose_name='Адрес доставки')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name='Способ оплаты')
    payment_status = models.CharField(max_length=255)
    comment = models.TextField(verbose_name='Комментарии к заказу')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость заказа')
    error_message = models.TextField(blank=True, null=True, verbose_name='Текст ошибки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания заказа')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='created', verbose_name='Статус заказа')

    class Meta:
        ordering = ['-created_at']

# Модель one-to-many Order - OrderItem с количеством товаров
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Ключ на заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Ключ на товар')
    quantity = models.IntegerField(default=1, verbose_name='Количество товаров')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, verbose_name='Ключ на продавца')

    class Meta:
        unique_together = ('order', 'product', 'seller')

# Модель истории просмотров
class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_view_history', verbose_name='Ключ на пользователя')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='view_history', verbose_name='Ключ на товар')
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата просмотра товара')

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ('user', 'product')

# Модель скидок
class Discount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discounts', verbose_name='Ключ на товар')
    description = models.TextField(verbose_name='Описание скидки')
    discount_percentage = models.FloatField(verbose_name='Процент скидки')
    start_date = models.DateTimeField(verbose_name='Дата начала скидки')
    end_date = models.DateTimeField(verbose_name='Дата окончания скидки')


# Модель отзывов
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews', verbose_name='Ключ на пользователя')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Ключ на товар')
    rating = models.IntegerField(verbose_name='Рейтинг отзыва')
    comment = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания отзыва')

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'product')
