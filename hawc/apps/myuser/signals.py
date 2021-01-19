from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def set_session_hero_access(sender, request, user, **kwargs):
    request.session["HERO_access"] = user.profile.HERO_access
