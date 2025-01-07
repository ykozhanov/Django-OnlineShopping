import re

from django import template

register = template.Library()

@register.filter
def ru_pluralize(value, arg):
    """
    Pluralizes a word based on the given number
    """
    args = arg.split(',')
    if len(args) != 3:
        return ''
    n = abs(int(value))
    if n % 10 == 1 and n % 100 != 11:
        return args[0]
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return args[1]
    else:
        return args[2]


@register.filter
def filter_by(value, args):
    """
    Filters a queryset to include only active reviews
    """
    filters = {}
    for pair in args.split(','):
        field, val = pair.split('=')
        filters[field.strip()] = val.strip()
    return value.filter(**filters)


@register.filter
def order_by(queryset, args):
    """
    Orders a queryset by the specified fields.
    """
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)


@register.filter()
def split_sentence(value):
    """
    Split the text into sentences based on .!?
    """
    sentence = re.split(r"(?<=[.!?]) +", value)
    return sentence