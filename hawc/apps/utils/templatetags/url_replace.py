from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """
    Add new parameters to a get URL.

    Example usage:
    <a href="?{% url_replace request 'page' paginator.next_page_number %}">

    Source: http://stackoverflow.com/questions/2047622/

    """
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()
