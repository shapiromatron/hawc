import pytest

from hawc.apps.myuser.forms import RegisterForm


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
        assert (
            form.errors["license_v2_accepted"][0]
            == "License must be accepted in order to create an account."
        )
