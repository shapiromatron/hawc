import re
from typing import Sequence
from urllib import parse

import bleach
from bleach.css_sanitizer import CSSSanitizer
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator
from django.utils.encoding import force_str

tag_regex = re.compile(r"</?(?P<tag>\w+)[^>]*>")
hyperlink_regex = re.compile(r"href\s*=\s*['\"](.*?)['\"]")

valid_html_tags = {
    "a",
    "blockquote",
    "br",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "li",
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
valid_html_attrs = {"*": ["style"], "a": ["href", "rel", "target"]}
valid_css_properties = {"color", "background-color"}
valid_scheme = {"", "http", "https"}
valid_netloc_endings = {
    ".gov",
    ".edu",
    ".who.int",
    "sciencedirect.com",
    "elsevier.com",
    "public.tableau.com",
}


def clean_html(html: str) -> str:
    """
    Cleans given HTML by removing invalid HTML tags, HTML properties, and CSS properties.

    Note: inner text within invalid HTML tags will still be included.

    Args:
        html (str): HTML to clean

    Returns:
        str: cleaned HTML
    """
    css_sanitizer = CSSSanitizer(allowed_css_properties=valid_css_properties)
    return bleach.clean(
        html,
        tags=valid_html_tags,
        attributes=valid_html_attrs,
        css_sanitizer=css_sanitizer,
        strip=True,
    )


def validate_html_tags(html: str, field: str = None) -> str:
    """Html contains a subset of acceptable tags.

    Args:
        html (str): html text to validate
        field (str, optional): field to use as key for error dict. Defaults to None.

    Raises:
        ValidationError if invalid tag found
    """
    html_tags = tag_regex.findall(html)
    invalid_html_tags = set(html_tags) - valid_html_tags
    if len(invalid_html_tags) > 0:
        err_msg = f"Invalid html tags: {', '.join(invalid_html_tags)}"
        raise ValidationError(err_msg if field is None else {field: err_msg})
    return html


def valid_url(url_str: str) -> bool:
    """Only allow URLs to some locations. Relative paths and a small subset of the internet domains are considered valid at this point; can increase the options with time.

    Args:
        url_str (str): The URL string

    Returns:
        bool: if URL can be used
    """
    url = parse.urlparse(url_str)
    if url.scheme not in valid_scheme:
        return False
    return url.netloc == "" or any(url.netloc.endswith(ending) for ending in valid_netloc_endings)


def validate_hyperlinks(html: str, field: str = None) -> str:
    """
    Validate that our hyperlinks are on the allowlist of acceptable link locations.

    This will be overly restrictive, but can be relaxed as requests are added.

    Args:
        html (str): html text to validate
        field (str, optional): field to use as key for error dict. Defaults to None.

    Raises:
        ValidationError: If any hyperlinks links to an invalid link location.

    Returns:
        If successful, the original html text, unmodified.
    """
    invalid_links = []
    for hyperlink in hyperlink_regex.findall(html):
        if not valid_url(hyperlink):
            invalid_links.append(hyperlink)
    if invalid_links:
        err_msg = f"Invalid hyperlinks: {', '.join(invalid_links)}"
        raise ValidationError(err_msg if field is None else {field: err_msg})
    return html


class CustomURLValidator(URLValidator):
    schemes = ["http", "https", "ftp", "ftps", "smb"]

    def __call__(self, value):
        value = force_str(value)
        # Check first if the scheme is valid
        scheme = value.split("://")[0].lower()
        if scheme not in self.schemes:
            raise ValidationError(self.message, code=self.code)

        if scheme == "smb":
            # assert valid URL, which is already URL quoted as needed
            abspath = value.split(":/")[1]
            if parse.quote(parse.unquote(abspath)) != abspath:
                raise ValidationError(self.message, code=self.code)
        else:
            super().__call__(value)


def validate_exact_ids(expected_ids: Sequence[int], ids: Sequence[int], name: str):
    """
    Valid that each and every ID is included in the sequence, with no additional IDs.

    Args:
        expected_ids (Sequence[int]): A sequence of expected IDs
        ids (Sequence[int]): A sequence of actual ids
        name (str): The name for describing validation errors
    """
    missing = set(expected_ids) - set(ids)
    extra = set(ids) - set(expected_ids)

    if missing:
        ids = ", ".join([str(v) for v in sorted(missing)])
        raise ValidationError(f"Missing ID(s) in {name}: {ids}")

    if extra:
        ids = ", ".join([str(v) for v in sorted(extra)])
        raise ValidationError(f"Extra ID(s) in {name}: {ids}")


class NumericTextValidator(RegexValidator):
    # alternative: r"^[<,≤,≥,>]? (?:LOD|[+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)$"
    regex = r"^[<,≤,≥,>]? ?(?:LOD|LOQ|[+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)$"
    message = "Must be number-like, including {<,≤,≥,>,LOD,LOQ} (ex: 3.4, 1.2E-5, < LOD)"
