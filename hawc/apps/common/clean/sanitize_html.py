"""Validate html."""

import nh3

from .sanitize_css import CSSSanitizer

valid_html_tags = {
    "a",
    "blockquote",
    "br",
    "div",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "li",
    "mark",
    "ol",
    "p",
    "span",
    "strong",
    "sub",
    "sup",
    "s",
    "ul",
    "u",
}

valid_html_attrs = {
    "*": {"style"},
    "a": {"class", "href"},
    "span": {"class"},
    "mark": {"class"},
    "div": {"class"},
}

valid_css_properties = {"color", "background-color"}
valid_svg_properties = {}

css_sanitizer = CSSSanitizer(
    allowed_css_properties=valid_css_properties,
    allowed_svg_properties=valid_svg_properties,
)


def clean_html(html: str) -> str:
    """Cleans given HTML by removing invalid HTML tags, attributes, and CSS properties.
    Note: inner text within invalid HTML tags will still be included.
    Args:
        html (str): HTML to clean
    Returns:
        str: cleaned HTML
    """

    def attribute_filter(element, attribute, value):
        """Send styles to CSS sanitizer."""
        if attribute == "style":
            return css_sanitizer.sanitize_css(value)
        return value

    return nh3.clean(
        html,
        tags=valid_html_tags,
        attributes=valid_html_attrs,
        attribute_filter=attribute_filter,
    )
