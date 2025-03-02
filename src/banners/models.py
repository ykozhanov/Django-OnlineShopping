from django.db import models

class Banner(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название баннера')
    image = models.ImageField(upload_to='banners/', verbose_name='Изображение')
    link = models.URLField(max_length=200, verbose_name='Ссылка', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    description = models.TextField(verbose_name='Banner description', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'banner'
        verbose_name_plural = 'banners'