from django.conf import settings


def from_settings(request):
    server_role = getattr(settings, "SERVER_ROLE", None)
    expire = request.session.get_expiry_date().isoformat() if request.user.is_authenticated else ""
    return dict(
        ADMIN_ROOT=settings.ADMIN_ROOT,
        SERVER_ROLE=server_role,
        SERVER_BANNER_COLOR=getattr(settings, "SERVER_BANNER_COLOR", "black"),
        session_expire_time=expire,
        commit=settings.COMMIT,
        flavor=settings.HAWC_FLAVOR,
        has_admin=settings.INCLUDE_ADMIN,
        GTM_ID=settings.GTM_ID,
        feature_flags=settings.HAWC_FEATURES,
    )
