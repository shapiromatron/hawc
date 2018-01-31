from django.core.exceptions import PermissionDenied
from myuser.models import HAWCUser

def epa_sso_authenticator(functionToCheck):
    def wrap(request, *args, **kwargs):
        # Check to see if the user is being re-directed from the EPA's Single-Sign-On portal
        HAWCUser.objects.lookup_by_epa_sso_uid(request)
        return functionToCheck(request, *args, **kwargs)

    wrap.__doc__ = functionToCheck.__doc__
    wrap.__name__ = functionToCheck.__name__

    return wrap
