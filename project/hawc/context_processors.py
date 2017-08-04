from django.conf import settings


def from_settings(request):
    SERVER_ROLE_TEXT = "" if settings.SERVER_ROLE == "production" else " (%s)" % settings.SERVER_ROLE
    return {
        'SERVER_ROLE': getattr(settings, 'SERVER_ROLE', None),
        'SERVER_ROLE_TEXT': SERVER_ROLE_TEXT,
        'SERVER_COLOR': getattr(settings, 'SERVER_COLOR', None),
    }
