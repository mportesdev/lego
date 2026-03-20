from django import template
from django.core.files.storage import storages

register = template.Library()


@register.filter
def is_static_file(rel_path):
    return rel_path is not None and storages["staticfiles"].exists(rel_path)
