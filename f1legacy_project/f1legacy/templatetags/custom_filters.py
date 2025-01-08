from django import template

register = template.Library()

@register.filter
def abs_value(value):
    """Return the absolute value of a number."""
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value
    
@register.filter
def format_position(value):
    if value == float('inf'):
        return '*'
    return value