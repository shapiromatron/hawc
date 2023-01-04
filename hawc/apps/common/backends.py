from django.contrib.auth.backends import BaseBackend
from rest_framework.authtoken.models import Token
from rest_framework.authentication import get_authorization_header

from hawc.apps.myuser.models import HAWCUser


class TokenBackend(BaseBackend):
    keyword = "Token"

    def get_token_from_header(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return
        if len(auth) != 2:
            return
        try:
            token = auth[1].decode()
        except UnicodeError:
            return

        return token

    def authenticate(self, request, token=None, **kwargs):
        if token is None:
            token = self.get_token_from_header(request)
        try:
            token_obj = Token.objects.select_related("user").get(key=token)
        except Token.DoesNotExist:
            return
        user = token_obj.user
        if not user.is_active:
            return
        return user

    def get_user(self, user_id):
        try:
            return HAWCUser.objects.get(pk=user_id)
        except HAWCUser.DoesNotExist:
            return None
