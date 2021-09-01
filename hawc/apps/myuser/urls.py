from django.urls import path, re_path

from . import api, views

app_name = "user"
urlpatterns = [
    path("login/", views.HawcLoginView.as_view(), name="login"),
    path("login/external-auth/", views.ExternalAuth.as_view(), name="external_auth"),
    path("logout/", views.HawcLogoutView.as_view(), name="logout"),
    path("new/", views.HawcUserCreate.as_view(), name="register"),
    path("profile/", views.ProfileDetail.as_view(), name="settings"),
    path("profile/update/", views.ProfileUpdate.as_view(), name="profile_update"),
    path("accept-new-license/", views.AcceptNewLicense.as_view(), name="accept-new-license",),
    path("password-change/", views.PasswordChange.as_view(), name="change_password"),
    path("password-reset/", views.HawcPasswordResetView.as_view(), name="reset_password",),
    path("password-reset/sent/", views.PasswordResetSent.as_view(), name="reset_password_sent",),
    re_path(
        r"^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
        views.HawcPasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    path(
        "password-reset-done/",
        views.HawcPasswordResetDoneView.as_view(),
        name="reset_password_done",
    ),
    path(
        "password-reset/complete/", views.PasswordResetSent.as_view(), name="reset_password_sent",
    ),
    path("password/changed/", views.PasswordChanged.as_view(), name="password_reset_complete",),
    path("<int:pk>/set-password/", views.SetUserPassword.as_view(), name="set_password",),
    path("api/token-auth/", api.hawc_obtain_auth_token, name="api_token_auth"),
]
