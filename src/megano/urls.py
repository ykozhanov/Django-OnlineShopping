"""
URL configuration for megano project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from megano.views import IndexView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sellers/", include("sellers.urls")),

    path("__debug__/", include("debug_toolbar.urls")),
    path('', IndexView.as_view(), name='index'),
    path('products/', include('products.urls')),
    path("accounts/", include('profiles.urls')),
    path("cart/", include('cart.urls')),
    path('banner/', include('banners.urls')),
    path('orders/', include('orders.urls')),
    path('compare/', include('comparison.urls')),
    path("discounts/", include("discounts.urls")),
    path("api/", include('paymentapi.urls'))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
