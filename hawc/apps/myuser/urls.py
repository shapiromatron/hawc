from django.urls import re_path

from . import api, views

app_name = "user"
urlpatterns = [
    re_path(r"^login/$", views.HawcLoginView.as_view(), name="login"),
    re_path(r"^logout/$", views.HawcLogoutView.as_view(), name="logout"),
    re_path(r"^new/$", views.HawcUserCreate.as_view(), name="register"),
    re_path(r"^profile/$", views.ProfileDetail.as_view(), name="settings"),
    re_path(r"^profile/update/$", views.ProfileUpdate.as_view(), name="profile_update"),
    re_path(r"^accept-new-license/$", views.AcceptNewLicense.as_view(), name="accept-new-license",),
    re_path(r"^password-change/$", views.PasswordChange.as_view(), name="change_password"),
    re_path(r"^password-reset/$", views.HawcPasswordResetView.as_view(), name="reset_password",),
    re_path(
        r"^password-reset/sent/$", views.PasswordResetSent.as_view(), name="reset_password_sent",
    ),
    re_path(
        r"^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$",
        views.HawcPasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
    re_path(
        r"^password-reset-done/$",
        views.HawcPasswordResetDoneView.as_view(),
        name="reset_password_done",
    ),
    re_path(
        r"^password-reset/complete/$",
        views.PasswordResetSent.as_view(),
        name="reset_password_sent",
    ),
    re_path(
        r"^password/changed/$", views.PasswordChanged.as_view(), name="password_reset_complete",
    ),
    re_path(r"^(?P<pk>\d+)/set-password/$", views.SetUserPassword.as_view(), name="set_password",),
    re_path(r"^api/token-auth/$", api.hawc_obtain_auth_token, name="api_token_auth"),
]
