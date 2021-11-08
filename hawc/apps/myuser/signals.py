import logging

from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from .models import HAWCUser

logger = logging.getLogger(__name__)


@receiver(user_logged_out)
def invalidate_tokens(sender, request, user: HAWCUser, **kw):
    user.destroy_api_token()
