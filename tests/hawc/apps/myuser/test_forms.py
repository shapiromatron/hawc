import pytest
from crispy_forms.utils import render_crispy_form
from pytest_django.asserts import assertInHTML

from hawc.apps.myuser.forms import (
    AcceptNewLicenseForm,
    AdminUserForm,
    HAWCPasswordResetForm,
    HAWCSetPasswordForm,
    RegisterForm,
    UserProfileForm,
    _accept_license_error,
)


@pytest.mark.django_db
class TestRegisterForm:
    def test_success(self):
        # simple case
        form = RegisterForm(
            {
                "email": "abc@def.com",
                "first_name": "",
                "last_name": "",
                "password1": "yp&9f7uDN2c8mRTX4",
                "password2": "yp&9f7uDN2c8mRTX4",
                "license_v2_accepted": True,
            }
        )
        assert form.is_valid()
        assert form.cleaned_data["email"] == "abc@def.com"

        # ensure uppercased-emails are lowercased
        form = RegisterForm(
            {
                "email": "ABC@DEF.COM",
                "first_name": "",
                "last_name": "",
                "password1": "yp&9f7uDN2c8mRTX4",
                "password2": "yp&9f7uDN2c8mRTX4",
                "license_v2_accepted": True,
            }
        )
        assert form.is_valid()
        assert form.cleaned_data["email"] == "abc@def.com"

        form.save()

        # assert password is salted and saved
        assert (
            form.instance.password.startswith("md5$")
            and form.instance.password != form.cleaned_data["password1"]
        )

        # assert profile is created
        assert form.instance.profile.id is not None

    def test_validation_failures_duplicates(self):
        form = RegisterForm(
            {
                "email": "pm@hawcproject.org",
                "first_name": "",
                "last_name": "",
                "password1": "yp&9f7uDN2c8mRTX4",
                "password2": "yp&9f7uDN2c8mRTX4",
                "license_v2_accepted": True,
            }
        )
        assert form.is_valid() is False
        assert form.errors["email"][0] == "HAWC user with this email already exists."

        form = RegisterForm(
            {
                "email": "pm@hawcproject.org",
                "first_name": "",
                "last_name": "",
                "password1": "yp&9f7uDN2c8mRTX4",
                "password2": "yp&9f7uDN2c8mRTX4",
                "license_v2_accepted": True,
            }
        )
        assert form.is_valid() is False
        assert form.errors["email"][0] == "HAWC user with this email already exists."

    def test_validation_failures_password(self):
        form = RegisterForm(
            {
                "email": "abc@def.com",
                "first_name": "",
                "last_name": "",
                "password1": "nope",
                "password2": "nope",
                "license_v2_accepted": True,
            }
        )
        assert form.is_valid() is False
        assert (
            form.errors["password1"][0]
            == "Password must be at least eight characters in length, at least one special character, and at least one digit."
        )

        form = RegisterForm(
            {
                "email": "abc@def.com",
                "first_name": "",
                "last_name": "",
                "password1": "yp&9f7uDN2c8mRTX4",
                "password2": "nope2",
                "license_v2_accepted": True,
            }
        )
        assert form.is_valid() is False
        assert form.errors["password2"][0] == "Passwords don't match"

    def test_validation_failures_license(self):
        form = RegisterForm(
            {
                "email": "abc@def.com",
                "first_name": "",
                "last_name": "",
                "password1": "yp&9f7uDN2c8mRTX4",
                "password2": "yp&9f7uDN2c8mRTX4",
                "license_v2_accepted": False,
            }
        )
        assert form.is_valid() is False
        assert form.errors["license_v2_accepted"][0] == _accept_license_error


@pytest.mark.django_db
class TestUserProfileForm:
    def test_success(self, pm_user):
        form = UserProfileForm(
            instance=pm_user.profile,
            data={"first_name": pm_user.first_name, "last_name": pm_user.last_name},
        )
        assert form.is_valid()
        form.save()


@pytest.mark.django_db
class TestAcceptNewLicenseForm:
    def test_render(self, pm_user):
        form = AcceptNewLicenseForm(instance=pm_user)
        html = render_crispy_form(form)
        assertInHTML("<legend>Please accept the terms of use</legend>", html)

    def test_failed(self, pm_user):
        form = AcceptNewLicenseForm(instance=pm_user, data=dict())
        assert not form.is_valid()
        assert "License must be accepted to continue." in form.errors["license_v2_accepted"][0]

    def test_success(self, pm_user):
        form = AcceptNewLicenseForm(instance=pm_user, data=dict(license_v2_accepted="on"))
        assert form.is_valid()


@pytest.mark.django_db
class TestHAWCSetPasswordForm:
    def test_render(self, pm_user):
        form = HAWCSetPasswordForm(user=pm_user)
        html = render_crispy_form(form)
        assertInHTML("Password reset", html)

    def test_success(self, pm_user):
        form = HAWCSetPasswordForm(
            user=pm_user, data=dict(new_password1="asdf@asdf123!", new_password2="asdf@asdf123!")
        )
        assert form.is_valid()

    def test_clean(self, pm_user):
        form = HAWCSetPasswordForm(
            user=pm_user, data=dict(new_password1="abc", new_password2="def")
        )
        assert not form.is_valid()
        assert (
            "Password must be at least eight characters in length"
            in form.errors["new_password1"][0]
        )


@pytest.mark.django_db
class TestHAWCPasswordResetForm:
    def test_success(self):
        form = HAWCPasswordResetForm(data=dict(email="pm@hawcproject.org"))
        assert form.is_valid()

    def test_failure(self):
        form = HAWCPasswordResetForm(data=dict(email="zzz@hawcproject.org"))
        assert not form.is_valid()
        assert "Email address not found" in str(form.errors)


@pytest.mark.django_db
class TestAdminUserForm:
    def test_render(self, pm_user):
        form = AdminUserForm()
        html = render_crispy_form(form)
        assertInHTML("First name", html)

    def test_success(self, pm_user):
        form = AdminUserForm(instance=pm_user, data={"email": pm_user.email})
        assert form.is_valid()
        form.save()
