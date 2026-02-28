from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Lookup value in dictionary by key"""
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        # If dictionary is not a dict or doesn't have get method
        if hasattr(dictionary, '__getitem__'):
            try:
                return dictionary[key]
            except (KeyError, IndexError, TypeError):
                pass
        return None