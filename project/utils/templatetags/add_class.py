import re
from django.utils.safestring import mark_safe
from django import template

register = template.Library()
class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')


@register.filter
def add_class(value, css_class):
    """http://djangosnippets.org/snippets/2253/
    Example call: {{field.name|add_class:"span4"}} """
    string = unicode(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class,
                                                    css_class, css_class), match.group(1))
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class,
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value
