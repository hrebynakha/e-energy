from django import template

register = template.Library()


@register.filter
def minutes_to_time(value):
    """Convert minutes since midnight to HH:MM"""
    if value is None:
        return ""
    hours = value // 60
    minutes = value % 60
    return f"{hours:02d}:{minutes:02d}"
