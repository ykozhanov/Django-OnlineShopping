from django import template

register = template.Library()

@register.filter
def filter_active(items):
    return [item for item in items if getattr(item, 'is_active', False)]

@register.filter
def filter_children(items, parent):
    return [item for item in items if getattr(item, 'parent', None) == parent ]