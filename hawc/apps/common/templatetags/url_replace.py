from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Add new parameters to a get URL, or removes if None.

    Example usage:
    <a href="?{% url_replace page=paginator.next_page_number %}">

    Source: http://stackoverflow.com/questions/2047622/

    """
    dict_ = context["request"].GET.copy()
    for key, value in kwargs.items():
        dict_[key] = value
        if value is None:
            dict_.pop(key)
    return dict_.urlencode()
