import re

from django.conf import settings

re_valid_agent = re.compile(r"chrome|firefox|edg|safari", re.IGNORECASE)


def is_supported_agent(ua: str) -> bool:
    """Check if user-agent is supported."""
    return bool(re_valid_agent.search(ua))


def from_settings(request):
    server_role = getattr(settings, "SERVER_ROLE", None)
    agent = request.headers.get("user-agent", "chrome")  # assume supported
    expire = request.session.get_expiry_date().isoformat() if request.user.is_authenticated else ""
    return dict(
        ADMIN_ROOT=settings.ADMIN_ROOT,
        SERVER_ROLE=server_role,
        SERVER_BANNER_COLOR=getattr(settings, "SERVER_BANNER_COLOR", "black"),
        UA_SUPPORTED=is_supported_agent(agent),
        session_expire_time=expire,
        commit=settings.COMMIT,
        flavor=settings.HAWC_FLAVOR,
        has_admin=settings.INCLUDE_ADMIN,
        GTM_ID=settings.GTM_ID,
        feature_flags=settings.HAWC_FEATURES,
    )
