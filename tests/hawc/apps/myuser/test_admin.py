import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from django.urls import reverse

from hawc.apps.myuser import admin as myuser_admin
from hawc.apps.myuser import models

from ..test_utils import get_user


@pytest.fixture
def rf():
    request = RequestFactory().get(reverse("admin:index"))
    request.session = "session"
    request._messages = FallbackStorage(request)
    return request


@pytest.fixture
def admin_instance():
    return myuser_admin.HAWCUserAdmin(models.HAWCUser, AdminSite())


@pytest.mark.django_db
def test_send_welcome_emails(admin_instance, rf):
    user = get_user("admin")
    queryset = models.HAWCUser.objects.filter(id=user.id)
    admin_instance.send_welcome_emails(request=rf, queryset=queryset)
    messages = [m.message for m in rf._messages]
    assert "Welcome email(s) sent!" in messages


@pytest.mark.django_db
def test_send_email_verification_email(admin_instance, rf):
    user = get_user("admin")
    queryset = models.HAWCUser.objects.filter(id=user.id)
    admin_instance.send_email_verification_email(request=rf, queryset=queryset)
    messages = [m.message for m in rf._messages]
    assert "Email verification email(s) sent!" in messages


@pytest.mark.django_db
class TestSetPassword:
    def test_set_password_external_auth(self, admin_instance, rf, settings):
        settings.AUTH_PROVIDERS = {myuser_admin.AuthProvider.external}
        user = get_user("admin")
        queryset = models.HAWCUser.objects.filter(id=user.id)

        admin_instance.set_password(request=rf, queryset=queryset)

        messages = [m.message for m in rf._messages]
        assert "Password cannot be set when using external auth" in messages

    @pytest.mark.django_db
    def test_set_password_single_user(self, admin_instance, rf, settings):
        settings.AUTH_PROVIDERS = {myuser_admin.AuthProvider.django}
        user = get_user("admin")
        queryset = models.HAWCUser.objects.filter(id=user.id)

        response = admin_instance.set_password(request=rf, queryset=queryset)

        assert response.status_code == 302
        assert "/set-password/" in response.url

    def test_set_password_multiple_users(self, admin_instance, rf, settings):
        settings.AUTH_PROVIDERS = {myuser_admin.AuthProvider.django}
        queryset = models.HAWCUser.objects.all()
        assert queryset.count() > 1

        admin_instance.set_password(request=rf, queryset=queryset)

        messages = [m.message for m in rf._messages]
        assert "Please select only-one user" in messages
