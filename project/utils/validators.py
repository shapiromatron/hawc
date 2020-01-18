from django.utils.encoding import force_text
from django.utils import http
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


class CustomURLValidator(URLValidator):
    schemes = ["http", "https", "ftp", "ftps", "smb"]

    def __call__(self, value):
        value = force_text(value)
        # Check first if the scheme is valid
        scheme = value.split("://")[0].lower()
        if scheme not in self.schemes:
            raise ValidationError(self.message, code=self.code)

        if scheme == "smb":
            # assert valid URL, which is already URL quoted as needed
            abspath = value.split(":/")[1]
            if http.urlquote(http.urlunquote(abspath)) != abspath:
                raise ValidationError(self.message, code=self.code)
        else:
            super().__call__(value)
