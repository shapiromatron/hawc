from django.conf.urls import url
from django.contrib.auth.views import (login, logout, password_reset,
                                       password_reset_done,
                                       password_reset_confirm)
from django.core.urlresolvers import reverse_lazy

from . import forms
from . import views


urlpatterns = [

    url(r'^login/$',
        login,
        {'authentication_form': forms.HAWCAuthenticationForm},
        'login'),
    url(r'^logout/$',
        logout,
        {'next_page': '/'},
        name='logout'),

    url(r'^new/$',
        views.create_account,
        name='new'),

    url(r'^profile/$',
        views.ProfileDetail.as_view(),
        name='settings'),
    url(r'^profile/update/$',
        views.ProfileUpdate.as_view(),
        name='profile_update'),
    url(r'^accept-new-license/$',
        views.AcceptNewLicense.as_view(),
        name='accept-new-license'),

    url(r'^password-change/$',
        views.PasswordChange.as_view(),
        name='change_password'),
    url(r'^password-reset/$', password_reset,
        {"post_reset_redirect": reverse_lazy("user:reset_password_sent"),
         "password_reset_form": forms.HAWCPasswordResetForm},
        name='reset_password'),
    url(r'^password-reset/sent/$',
        views.PasswordResetSent.as_view(),
        name='reset_password_sent'),
    url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        password_reset_confirm,
        {
            "set_password_form": forms.HAWCSetPasswordForm,
            "post_reset_redirect": reverse_lazy("user:password_reset_complete")
        },
        name='reset_password_confirm'),
    url(r'^password-reset-done/$',
        password_reset_done,
        name='reset_password_done'),
    url(r'^password-reset/complete/$',
        views.PasswordResetSent.as_view(),
        name='reset_password_sent'),
    url(r'^password/changed/$',
        views.PasswordChanged.as_view(),
        name='password_reset_complete'),

    url(r'^(?P<pk>\d+)/set-password/$',
        views.SetUserPassword.as_view(),
        name='set_password'),
]
