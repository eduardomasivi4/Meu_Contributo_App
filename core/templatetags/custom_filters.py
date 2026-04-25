# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retorna o valor de um dicionário para a chave fornecida"""
    if dictionary is None:
        return 0
    return dictionary.get(str(key), 0)