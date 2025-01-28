from django.db.models import Min

from django import template

register = template.Library()

@register.simple_tag
def get_min_price(value):
    """
    Tag for find min price
    """
    min_price = value.sellers.aggregate(min_price=Min('price'))['min_price']
    return min_price



