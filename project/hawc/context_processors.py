from django.conf import settings


def from_settings(request):

    server_role = getattr(settings, 'SERVER_ROLE', None)

    return dict(
        SERVER_ROLE=server_role,
        SERVER_BANNER_COLOR=getattr(settings, 'SERVER_BANNER_COLOR', 'black'),
    )
