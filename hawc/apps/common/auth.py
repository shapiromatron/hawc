from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token


class TokenBackend(ModelBackend):
    keyword = "Token"

    def get_token_from_header(self, request) -> str:
        auth = get_authorization_header(request).split()
        token = ""
        if auth and auth[0].lower() == self.keyword.lower().encode() and len(auth) == 2:
            try:
                token = auth[1].decode()
            except UnicodeError:
                pass
        return token

    def authenticate(self, request, token=None, **kwargs):
        if request is not None and token is None:
            token = self.get_token_from_header(request)
        if not token:
            return None
        try:
            token_obj = Token.objects.select_related("user").get(key=token)
        except Token.DoesNotExist:
            return
        return token_obj.user if self.user_can_authenticate(token_obj.user) else None
