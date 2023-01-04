from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token


class TokenBackend(ModelBackend):
    keyword = "Token"

    def get_token_from_header(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode() or len(auth) != 2:
            return
        try:
            token = auth[1].decode()
        except UnicodeError:
            return

        return token

    def authenticate(self, request, token=None, **kwargs):
        if request is not None and token is None:
            token = self.get_token_from_header(request)
        try:
            token_obj = Token.objects.select_related("user").get(key=token)
        except Token.DoesNotExist:
            return
        return token_obj.user if self.user_can_authenticate(token_obj.user) else None
