import pytest
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.test.client import Client
from django.urls import reverse

from hawc.apps.myuser import models
from hawc.apps.myuser.forms import _accept_license_error
from hawc.apps.myuser.views import ExternalAuth


class UserCreationTests(TestCase):
    def test_validation_errors(self):
        # assert various errors are present
        view = "user:register"
        c = Client()
        response = c.post(
            reverse(view),
            {
                "email": "not_email_address",
                "first_name": "John",
                "last_name": "Malcovich",
                "password1": "simple",
                "password2": "simple",
                "license_v2_accepted": "",
            },
        )
        self.assertFormError(response.context["form"], "email", "Enter a valid email address.")
        self.assertFormError(
            response.context["form"],
            "license_v2_accepted",
            _accept_license_error,
        )
        self.assertFormError(
            response.context["form"],
            "password1",
            "Password must be at least eight characters in length, at least one special character, and at least one digit.",
        )

    def test_password_match(self):
        # password-match check
        view = "user:register"
        c = Client()
        response = c.post(
            reverse(view),
            {
                "email": "foo@bar.com",
                "first_name": "John",
                "last_name": "Malcovich",
                "password1": "abcEasy@s123",
                "password2": "abcEasy@s1234",
                "license_v2_accepted": "t",
            },
        )
        self.assertFormError(response.context["form"], "password2", "Passwords don't match")

    def test_duplicate_email(self):
        # confirm that you can't create two accounts with the same email
        view = "user:register"
        email = "duplicate_email@gmail.com"
        form_dict = {
            "email": email,
            "first_name": "John",
            "last_name": "Malcovich",
            "password1": "abcEasy@s123",
            "password2": "abcEasy@s123",
            "license_v2_accepted": "t",
        }

        c = Client()
        response = c.post(reverse(view), form_dict)
        self.assertTrue(models.HAWCUser.objects.filter(email=email).exists())

        c2 = Client()
        response = c2.post(reverse(view), form_dict)
        self.assertFormError(response.context["form"], "email", "HAWC user with this email already exists.")

    def test_long_email_success(self):
        # confirm you can use a long email address, 200+characters
        view = "user:register"
        c = Client()
        email = "a" * 200 + "@gmail.com"
        c.post(
            reverse(view),
            {
                "email": email,
                "first_name": "John",
                "last_name": "Malcovich",
                "password1": "asdf@asdf1",
                "password2": "asdf@asdf1",
                "license_v2_accepted": "true",
            },
        )
        self.assertTrue(models.HAWCUser.objects.filter(email=email).exists())


@pytest.mark.django_db
class TestLoginView:
    def test_create_account_link(self):
        # default case
        c = Client()
        resp = c.get(reverse("user:login"))
        assert settings.HAWC_FEATURES.ANONYMOUS_ACCOUNT_CREATION is True
        assert b"Create an account" in resp.content
        resp = c.get(reverse("user:register")).status_code == 200

        # override case
        settings.HAWC_FEATURES.ANONYMOUS_ACCOUNT_CREATION = False
        resp = c.get(reverse("user:login"))
        assert b"Create an account" not in resp.content
        resp = c.get(reverse("user:register")).status_code == 404

        settings.HAWC_FEATURES.ANONYMOUS_ACCOUNT_CREATION = True

    @pytest.mark.vcr
    def test_turnstyle(self, settings):
        url = reverse("user:login")
        success = {"username": "pm@hawcproject.org", "password": "pw"}

        # no turnstyle by default
        c = Client()
        resp = c.get(url)
        assert b"challenges.cloudflare.com/turnstile" not in resp.content
        assert b'data-sitekey="https://test-me.org"' not in resp.content
        resp = c.post(url, data=success)
        assert resp.status_code == 302
        assert resp.url == "/portal/"

        # turnstyle if enabled
        c = Client()
        settings.TURNSTYLE_SITE = "https://test-me.org"
        settings.TURNSTYLE_KEY = "secret"
        resp = c.get(url)
        assert b"challenges.cloudflare.com/turnstile" in resp.content
        assert b'data-sitekey="https://test-me.org"' in resp.content
        resp = c.post(url, data=success)
        assert resp.status_code == 200
        assert resp.context["form"].errors == {"__all__": ["Failed bot challenge - are you human?"]}


class ExternalAuthSetup(ExternalAuth):
    # mock user metdata handler for test case
    def get_user_metadata(self, request):
        return {
            "email": request.headers["Email"],
            "external_id": request.headers["Id"],
            "first_name": request.headers["Firstname"],
            "last_name": request.headers["Lastname"],
        }


class ExternalAuthTests(TestCase):
    request_factory = RequestFactory()
    middleware = SessionMiddleware()

    def _login(self, email, external_id):
        headers = {
            "HTTP_EMAIL": email,
            "HTTP_ID": external_id,
            "HTTP_FIRSTNAME": "John",
            "HTTP_LASTNAME": "Doe",
        }
        request = self.request_factory.get("/", **headers)
        self.middleware.process_request(request)
        return ExternalAuthSetup.as_view()(request)

    def test_valid_auth(self):
        email = "pm@hawcproject.org"
        external_id = "pm"
        # If email is associated with user then user is logged in
        response = self._login(email, external_id)
        assert response.status_code == 302
        user = models.HAWCUser.objects.get(email=email)
        assert user.is_authenticated
        # External id is also set on the user
        assert user.external_id == external_id

    def test_create_user(self):
        email = "new_user@hawcproject.org"
        external_id = "nu"
        # If user doesn't exist, it should be created and logged in
        response = self._login(email, external_id)
        assert response.status_code == 302
        user = models.HAWCUser.objects.get(email=email)
        assert user.is_authenticated and user.external_id == external_id
        assert user.first_name == "John" and user.last_name == "Doe"

    def test_invalid_auth(self):
        # Fails if headers are invalid / missing
        forbidden_url = reverse("401")
        request = self.request_factory.get("/")
        response = ExternalAuthSetup.as_view()(request)
        assert response.status_code == 302 and response.url == forbidden_url

        # Fails if email/external_id doesn't match
        email = "new_user@hawcproject.org"
        external_id = "nu"
        self._login(email, external_id)  # Creates the user
        bad_external_id = "wrong_id"
        response = self._login(email, bad_external_id)
        assert response.status_code == 302 and response.url == forbidden_url

        # Fails if email doesn't match external_id
        bad_email = "another_user@hawcproject.org"
        response = self._login(bad_email, external_id)
        assert response.status_code == 302 and response.url == forbidden_url
