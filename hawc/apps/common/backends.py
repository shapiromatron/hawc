from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token


class HawcBackend(ModelBackend):
    keyword = "Token"

    def get_auth_token(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return
        if len(auth) != 2:
            return
        try:
            token_key = auth[1].decode()
        except UnicodeError:
            return
        try:
            token = Token.objects.select_related("user").get(key=token_key)
        except Token.DoesNotExist:
            return
        if not token.user.is_active:
            return
        return token

    def authenticate(self, request, username=None, password=None, **kwargs):

        user = super().authenticate(request, username, password, **kwargs)

        if user is None:
            token = self.get_auth_token(request)

            return token.user if token else None
        return user
