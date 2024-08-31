import re
from collections.abc import Callable, Sequence
from functools import partial
from urllib import parse

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator
from django.utils.encoding import force_str
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from .clean.sanitize_html import valid_html_tags

tag_regex = re.compile(r"</?(?P<tag>\w+)[^>]*>")
hyperlink_regex = re.compile(r"href\s*=\s*['\"](.*?)['\"]")
valid_scheme = {"", "http", "https"}
valid_netloc_endings = {
    "canada.ca",
    ".edu",
    ".gov",
    ".who.int",
    "doi.org",
    "elsevier.com",
    "public.tableau.com",
    "sciencedirect.com",
    "sharepoint.com",
    "hawcproject.org",
    "zenodo.org",
}


def validate_html_tags(html: str, field: str | None = None) -> str:
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


def validate_hyperlink(value: str, raise_exception: bool = True) -> bool:
    """Only allow URLs to some locations. Relative paths and a small subset of the internet domains are considered valid at this point; can increase the options with time.

    Args:
        value (str): The URL string
        raise_exception (bool, default True): Raise an exception if an invalid hyperlink

    Raises:
        ValidationError: If not valid and raise_exception is True

    Returns:
        bool: if URL can be used
    """
    url = parse.urlparse(value)
    valid = url.scheme in valid_scheme and (
        url.netloc == "" or any(url.netloc.endswith(ending) for ending in valid_netloc_endings)
    )
    if url.netloc == "" and ("." in url.path or not url.path.endswith("/")):
        valid = False
    if raise_exception and not valid:
        raise ValidationError(f"Invalid hyperlink: {value}")
    return valid


def validate_hyperlinks(html: str, field: str | None = None) -> str:
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
        if not validate_hyperlink(hyperlink, raise_exception=False):
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


class ColorValidator(RegexValidator):
    regex = r"^#[a-f0-9]{6}$"
    flags = re.IGNORECASE
    message = "Must be in #rrggbb hexadecimal format."


class FlatJSON:
    """A JSON based-field where all key and values are strings."""

    HELP_TEXT = """A <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON">JSON</a> object where keys are strings and values are strings or numbers. For example, <code>{"Player": "Michael Jordan", "Number": 23}</code>."""
    ERROR_MSG = "Flat JSON object required; arrays and nested objects are not valid."

    @classmethod
    def validate(cls, value: dict, raise_exception: bool = True) -> bool:
        """Validate that all keys are values are strings and only strings

        Args:
            value (str): The dictionary
            raise_exception (bool, optional): Defaults to True.

        Raises:
            ValidationError: If not valid and raise_exception is True

        Returns:
            bool: if validation is successful
        """
        valid = True

        if not isinstance(value, dict):
            raise ValidationError(cls.ERROR_MSG)
        for key, val in value.items():
            if not isinstance(key, str) or isinstance(val, list | dict):
                valid = False
                break
        if valid is False and raise_exception:
            raise ValidationError(cls.ERROR_MSG)
        return valid


def _validate_json_pydantic(value: str, Model: type[BaseModel]):
    """Validate a JSON string to ensure it conforms to a pydantic model

    Args:
        value (str): an input string
        Model (type[BaseModel]): A matching pydantic schema

    Raises:
        django.core.exceptions.ValidationError: If data do not conform
    """
    try:
        Model.model_validate_json(value)
    except PydanticValidationError as err:
        raise ValidationError(err.json()) from err


def validate_json_pydantic(Model: type[BaseModel]) -> Callable:
    """Create a django validator function to validate JSON in a string field

    Args:
        Model (type[BaseModel]): A Pydantic model class

    Returns:
        Callable: A django validator function to be used in a form or model
    """
    return partial(_validate_json_pydantic, Model=Model)
