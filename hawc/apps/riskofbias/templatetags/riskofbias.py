from django import template
from django.utils.safestring import mark_safe

from ..constants import SCORE_CHOICES_MAP, SCORE_SHADES, SCORE_SYMBOLS

register = template.Library()

DARK_SHADES = {"#CC3333", "#00441b"}


@register.simple_tag()
def score_option(id: int) -> str:
    background = SCORE_SHADES[id]
    color = "white" if background in DARK_SHADES else "auto"
    return mark_safe(
        f'<li class="my-2"><span class="d-inline-block py-1 mr-2 text-center" style="width: 50px; color: {color}; background: {background}">{SCORE_SYMBOLS[id]}</span>{SCORE_CHOICES_MAP[id]}</li>'
    )
