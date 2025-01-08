import os
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def category_icon_directory_path(instance: 'Category', filename: str):
    file_extension: str = filename.split('.')[-1]
    return 'categories/{id}.{extension}'.format(
        id=instance.id,
        extension=file_extension,
    )

def product_image_directory_path(instance: 'Product', filename: str):
    file_extension: str = filename.split('.')[-1]
    return 'products/{id}.{extension}'.format(
        id=instance.id,
        extension=file_extension,
    )

class Category(MPTTModel):
    """Product category model"""

    class Meta:
        # ordering = ['sort_index', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    class MPTTMeta:
        order_insertion_by = ['sort_index', 'name']

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name='children',
        verbose_name='Parent category',
    )
    name=models.CharField(
        max_length=255,
        verbose_name='Category name',
    )
    description=models.TextField(
        null=False,
        blank=True,
        verbose_name='Category description',
    )
    icon=models.ImageField(
        null=True,
        blank=True,
        upload_to=category_icon_directory_path,
        verbose_name='Category icon',
    )
    is_active=models.BooleanField(
        default=True,
        verbose_name='Is category active',
    )
    sort_index = models.IntegerField(
        default=0,
        verbose_name='Sort index',
    )

    def __str__(self):
        return f'{self.name}'
    
    def save(self, *args, **kwargs):
        """Save method redefinition to firstly get category id and then get path to icon"""
        is_new: bool = self.id is None
        if not is_new:
            old_icon = Category.objects.filter(pk=self.pk).first().icon
            if old_icon and self.icon != old_icon:
                if old_icon.path and os.path.exists(old_icon.path):
                    os.remove(old_icon.path)
        super().save(*args, **kwargs)
        if is_new and self.icon:
            new_icon_path: str = category_icon_directory_path(self, self.icon.name)
            self.icon.storage.save(new_icon_path, self.icon.file)
            self.icon.name = new_icon_path
            super().save(update_fields=['icon'])


class TagModel(models.Model):
    """
    Tag model
    """
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'tags'

    name = models.CharField(max_length=20, verbose_name='Tag name')

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    """Product model"""

    class Meta:
        ordering = ['sort_index', 'name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    category = TreeForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Product category',
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Product name',
    )
    description = models.TextField(
        null=False,
        blank=True,
        verbose_name='Product description',
    )
    short_description = models.CharField(
        max_length=200,
        null=False,
        blank=True,
        verbose_name='Product short description'
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=product_image_directory_path,
        verbose_name='Product image',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Product adding date'
    )
    sort_index = models.IntegerField(
        default=0,
        verbose_name='Sort index',
    )
    limited_edition = models.BooleanField(
        default=False,
        verbose_name='Limited edition flag',
    )
    is_active=models.BooleanField(
        default=True,
        verbose_name='Is product active',
    )

    def __str__(self):
        return f'{self.name}'
    
    def save(self, *args, **kwargs):
        """Save method redefinition to firstly get product id and then get path to icon"""
        is_new: bool = self.id is None
        if not is_new:
            old_image = Product.objects.filter(pk=self.pk).first().image
            if old_image and self.image != old_image:
                if old_image.path and os.path.exists(old_image.path):
                    os.remove(old_image.path)
        super().save(*args, **kwargs)
        if is_new and self.image:
            new_image_path: str = product_image_directory_path(self, self.image.name)
            self.image.storage.save(new_image_path, self.image.file)
            self.image.name = new_image_path
            super().save(update_fields=['image'])


class Characteristic(models.Model):
    """Characteristic model"""

    CHARACTERISTIC_TYPES = [
        ('string', 'String value type'),
        ('integer', 'Integer value type'),
        ('float', 'Float value type'),
    ]

    class Meta:
        ordering = ['name']
        verbose_name = 'Characteristic'
        verbose_name_plural = 'Characteristics'

    name = models.CharField(
        max_length=50,
        verbose_name='Category characteristic',
    )
    value_type = models.CharField(
        max_length=255,
        choices=CHARACTERISTIC_TYPES,
        default='string',
        verbose_name='Type of characteristic value',
    )
    
    def __str__(self):
        return f'{self.name}'


class ProductCharacteristicValue(models.Model):
    """Product characteristic model with specific value"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='characteristic_values',
        verbose_name='Product',
    )
    characteristic = models.ForeignKey(
        Characteristic,
        on_delete=models.CASCADE,
        related_name='characteristic_values',
        verbose_name='Product characteristic',
    )
    value = models.CharField(
        max_length=255,
        verbose_name='Characteristic value',
    )


class SiteSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="Key")
    value = models.TextField(verbose_name="Value")

    class Meta:
        verbose_name = "Site setting"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return f"{self.key}: {self.value}"

    @staticmethod
    def get_or_create_default( key, default=None):
        setting, created = SiteSetting.objects.get_or_create(
            key=key,
            defaults={'value': default}
        )
        return setting.value


class ReviewModel(models.Model):
    """
    Review model
    """
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000, verbose_name='Review text')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Review is active ")

    def __str__(self):
        return f'Review by {self.user.username} on {self.product.name}'


class ViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='view_history')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} просмотрел {self.product.name} в {self.viewed_at}"


class ProductTagsModel(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_tags',
        verbose_name='Product',
    )
    tag = models.ForeignKey(
        TagModel,
        on_delete=models.CASCADE,
        related_name='product_tags',
        verbose_name='Tag',
    )

