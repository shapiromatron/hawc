from urllib import parse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.encoding import force_str


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
