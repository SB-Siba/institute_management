from django import template

register = template.Library()

@register.filter
def dict_key(dictionary, key):
    return dictionary.get(key)

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})