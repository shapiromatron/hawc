import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag()
def highlight_tokens(topic, text: str) -> str:
    """Mark text with selected tokens as highlighted color.
    Begin by adding HTML to all tokens at once, then add correct class.
    Bulk marking all tokens with base html in the beginning allows
    'mark' and 'class' to be used as tokens without side effects
    """
    positive_tokens = topic.positive_tokens()
    negative_tokens = topic.negative_tokens()
    all_tokens = positive_tokens + negative_tokens
    # exit early if we dont have any tokens
    if not all_tokens:
        return mark_safe(text)
    # replace all tokens with HTML tagged tokens at once
    text = re.sub(
        rf"(?P<token>{'|'.join(all_tokens)})", r"<mark>\g<token></mark>", text, flags=re.IGNORECASE
    )
    # add correct class to positive HTML tagged tokens
    text = re.sub(
        rf"<mark>(?P<token>{'|'.join(positive_tokens)})</mark>",
        r"<mark class='hawc-mk-pos'>\g<token></mark>",
        text,
        flags=re.IGNORECASE,
    )
    # add correct class to negative HTML tagged tokens
    text = re.sub(
        rf"<mark>(?P<token>{'|'.join(negative_tokens)})</mark>",
        r"<mark class='hawc-mk-neg'>\g<token></mark>",
        text,
        flags=re.IGNORECASE,
    )
    return mark_safe(text)
