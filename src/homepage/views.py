from django.shortcuts import render
from django.views.generic import TemplateView

from products.models import Category


class HomepageTemplateView(TemplateView):
    template_name = "index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_category_list"] = Category.objects.all()
        return context
