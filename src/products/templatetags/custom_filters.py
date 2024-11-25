from django import template

register = template.Library()

@register.filter
def ru_pluralize(value, arg):
    """
    Склоняет слово в зависимости от числа
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
