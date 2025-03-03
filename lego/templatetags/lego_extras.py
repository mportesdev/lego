from django import template
from django.conf import settings

register = template.Library()


@register.filter
def is_static_file(rel_path):
    return rel_path is not None and (settings.STATIC_ROOT / rel_path).is_file()
