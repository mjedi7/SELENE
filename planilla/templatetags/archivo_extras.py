from django import template

register = template.Library()

@register.filter
def filesizeformat(bytes_value):
    try:
        bytes_value = int(bytes_value)
        if bytes_value < 1024:
            return f"{bytes_value} B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.1f} KB"
        else:
            return f"{bytes_value / (1024 * 1024):.2f} MB"
    except Exception:
        return "—"
