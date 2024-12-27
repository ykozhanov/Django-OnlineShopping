from django.shortcuts import render
from .models import Banner

def index(request):
    banners = Banner.objects.filter(is_active=True)
    return render(request, 'banners/banners.html', {'banners': banners})