from django.conf import settings
from django.urls import path, re_path

from ...constants import AuthProvider
from . import api, views

app_name = "user"

urlpatterns = [
    path("login/", views.HawcLoginView.as_view(), name="login"),
    path("logout/", views.HawcLogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileDetail.as_view(), name="settings"),
    path("profile/update/", views.ProfileUpdate.as_view(), name="profile_update"),
    path("accept/", views.AcceptNewLicense.as_view(), name="accept-license",),
]

if AuthProvider.django in settings.AUTH_PROVIDERS:
    urlpatterns += [
        path("register/", views.HawcUserCreate.as_view(), name="register"),
        path("password-change/", views.PasswordChange.as_view(), name="change_password"),
        path("password-reset/", views.HawcPasswordResetView.as_view(), name="reset_password",),
        path(
            "password-reset/sent/", views.PasswordResetSent.as_view(), name="reset_password_sent",
        ),
        re_path(
            r"^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
            views.HawcPasswordResetConfirmView.as_view(),
            name="reset_password_confirm",
        ),
        path(
            "password-reset/done/",
            views.HawcPasswordResetDoneView.as_view(),
            name="reset_password_done",
        ),
        path(
            "password-reset/complete/",
            views.PasswordResetSent.as_view(),
            name="reset_password_sent",
        ),
        path("password/changed/", views.PasswordChanged.as_view(), name="password_reset_complete",),
        path("<int:pk>/set-password/", views.SetUserPassword.as_view(), name="set_password",),
        path("api/token-auth/", api.hawc_obtain_auth_token, name="api_token_auth"),
    ]

if AuthProvider.external in settings.AUTH_PROVIDERS:
    urlpatterns += [
        path("login/wam/", views.ExternalAuth.as_view(), name="external_auth"),
    ]
