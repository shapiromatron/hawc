import re
from urllib import parse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.encoding import force_str

tag_regex = re.compile(r"</?(?P<tag>\w+)[^>]*>")

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
