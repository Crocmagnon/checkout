from django import template

register = template.Library()


@register.filter
def currency(value):
    if isinstance(value, int | float):
        return f"{value/100:.2f}€"
    return value
