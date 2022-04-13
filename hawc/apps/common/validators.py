import re
from typing import Sequence
from urllib import parse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.encoding import force_str

tag_regex = re.compile(r"</?(?P<tag>\w+)[^>]*>")
hyperlink_regex = re.compile(r"href\s*=\s*['\"](.*?)['\"]")

valid_html_tags_re = {
    "a",
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
    "ul",
    "u",
}
valid_scheme = {"", "http", "https"}
valid_netloc_endings = {
    ".gov",
    ".edu",
    ".who.int",
    "sciencedirect.com",
    "elsevier.com",
    "public.tableau.com",
}


def validate_html_tags(text: str) -> str:
    """Html contains a subset of acceptable tags.

    Raises:
        ValidationError if invalid tag found
    """
    html_tags = tag_regex.findall(text)
    invalid_html_tags = set(html_tags) - valid_html_tags_re
    if len(invalid_html_tags) > 0:
        raise ValidationError({"content": f"Invalid html tags: {', '.join(invalid_html_tags)}"})
    return text


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


def validate_hyperlinks(html: str) -> str:
    """
    Validate that our hyperlinks are on the allowlist of acceptable link locations.

    This will be overly restrictive, but can be relaxed as requests are added.

    Args:
        html (str): html text to validate

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
        raise ValidationError({"content": f"Invalid hyperlinks: {', '.join(invalid_links)}"})
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
