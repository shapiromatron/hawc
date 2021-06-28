from crispy_forms import layout as cfl
from django import forms
from django.contrib.auth import get_backends
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.forms import ModelForm
from django.urls import reverse

from ..assessment import lookups
from ..common.forms import BaseFormHelper
from ..common.selectable import AutoCompleteSelectMultipleField
from . import models

_PASSWORD_HELP = (
    "Password must be at least eight characters in length, "
    + "at least one special character, and at least one digit."
)


def checkPasswordComplexity(pw):
    special_characters = r"""~!@#$%^&*()_-+=[]{};:'"\|,<.>/?"""
    if (
        (len(pw) < 8)
        or (not any(char.isdigit() for char in pw))
        or (not any(char in special_characters for char in pw))
    ):
        raise forms.ValidationError(_PASSWORD_HELP)


class PasswordForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password", widget=forms.PasswordInput, help_text=_PASSWORD_HELP
    )
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = models.HAWCUser
        fields = ("password1", "password2")

    def clean_password1(self):
        pw = self.cleaned_data["password1"]
        if not self.fields["password1"].required and pw == "":
            return pw
        checkPasswordComplexity(pw)
        return pw

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if not self.fields["password2"].required and password2 == "":
            return password2
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        if self.cleaned_data["password1"] != "":
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class HAWCSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = _PASSWORD_HELP

    @property
    def helper(self):
        cancel_url = reverse("user:login")
        helper = BaseFormHelper(
            self,
            legend_text="Password reset",
            help_text="Enter a new password for your account.",
            form_actions=[
                cfl.Submit("submit", "Change password"),
                cfl.HTML(f'<a role="button" class="btn btn-light" href="{cancel_url}">Cancel</a>'),
            ],
        )
        return helper

    def clean_new_password1(self):
        pw = self.cleaned_data["new_password1"]
        checkPasswordComplexity(pw)
        return pw


class HAWCPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].help_text = _PASSWORD_HELP

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Change your password",
            help_text="Enter a new password for your account.",
            cancel_url=reverse("user:settings"),
        )
        return helper

    def clean_new_password1(self):
        pw = self.cleaned_data["new_password1"]
        checkPasswordComplexity(pw)
        return pw


class RegisterForm(PasswordForm):
    _accept_license_help_text = "License must be accepted in order to create an account."

    class Meta:
        model = models.HAWCUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "license_v2_accepted",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["license_v2_accepted"].label = "Accept license"
        self.fields["license_v2_accepted"].help_text = self._accept_license_help_text
        txt = '&nbsp;<a href="#" data-toggle="modal" data-target="#license_modal">View license</a>'
        self.fields["license_v2_accepted"].help_text += txt

    @property
    def helper(self):
        login_url = reverse("user:login")
        helper = BaseFormHelper(
            self,
            legend_text="Create an account",
            form_actions=[
                cfl.Submit("login", "Create account"),
                cfl.HTML(f'<a role="button" class="btn btn-light" href="{login_url}">Cancel</a>'),
            ],
        )
        helper.add_row("first_name", 2, "col-6")
        helper.add_row("password1", 2, "col-6")
        return helper

    def clean_license_v2_accepted(self):
        license = self.cleaned_data.get("license_v2_accepted")
        if not license:
            raise forms.ValidationError(self._accept_license_help_text)
        return license

    def clean_email(self):
        email = self.cleaned_data.get("email").strip().lower()
        if models.HAWCUser.objects.filter(email__iexact=email).count() > 0:
            raise forms.ValidationError("HAWC user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            user.create_profile()
        return user


class UserProfileForm(ModelForm):

    first_name = forms.CharField(label="First name", required=True)
    last_name = forms.CharField(label="Last name", required=True)

    class Meta:
        model = models.UserProfile
        fields = ("first_name", "last_name", "HERO_access")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name

    @property
    def helper(self):
        helper = BaseFormHelper(
            self,
            legend_text="Update your profile",
            help_text="Change settings associated with your account",
            cancel_url=reverse("user:settings"),
        )
        return helper

    def save(self, commit=True):
        # save content to both UserProfile and User
        up = super().save(commit=False)
        up.user.first_name = self.cleaned_data["first_name"]
        up.user.last_name = self.cleaned_data["last_name"]
        if commit:
            up.save()
            up.user.save()
        return up


class AcceptNewLicenseForm(ModelForm):
    class Meta:
        model = models.HAWCUser
        fields = ("license_v2_accepted",)


def hawc_authenticate(email=None, password=None):
    """
    If the given credentials are valid, return a User object.
    From: http://www.shopfiber.com/case-insensitive-username-login-in-django/
    """
    backend = get_backends()[0]  # only works if one backend
    try:
        user = models.HAWCUser.objects.get(email__iexact=email)
        if user.check_password(password):
            # Annotate the user object with the path of the backend.
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            return user
        else:
            return None
    except models.HAWCUser.DoesNotExist:
        return None


class HAWCAuthenticationForm(AuthenticationForm):
    """
    Modified to do a case-insensitive comparison of emails.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def helper(self):
        return BaseFormHelper(
            self,
            legend_text="HAWC login",
            form_actions=[
                cfl.Submit("login", "Login"),
                cfl.HTML(
                    f"""
                <a role="button" class="btn btn-light" href="{reverse("home")}">Cancel</a>
                <br>
                <br>
                <a href="{reverse("user:reset_password")}">Forgot your password?</a>
                <br>
                <a href="{reverse("user:register")}">Create an account</a>
                <br>
                """
                ),
            ],
        )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            self.user_cache = hawc_authenticate(email=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"]
                    % {"username": self.username_field.verbose_name}
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages["inactive"])
        return self.cleaned_data


class HAWCPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].help_text = "Email-addresses are case-sensitive."

    @property
    def helper(self):
        return BaseFormHelper(
            self,
            legend_text="Password reset",
            help_text="Enter your email address below, and we'll email instructions for setting a new password.",
            form_actions=[
                cfl.Submit("submit", "Send email confirmation"),
                cfl.HTML(
                    f'<a role="button" class="btn btn-secondary" href="{reverse("user:login")}">Cancel</a>'
                ),
            ],
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            models.HAWCUser.objects.get(email=email)
        except models.HAWCUser.DoesNotExist:
            raise forms.ValidationError("Email address not found")

        return email


class AdminUserForm(PasswordForm):

    project_manager = AutoCompleteSelectMultipleField(
        lookup_class=lookups.AssessmentLookup, label="Project manager", required=False
    )
    team_member = AutoCompleteSelectMultipleField(
        lookup_class=lookups.AssessmentLookup, label="Team member", required=False
    )
    reviewer = AutoCompleteSelectMultipleField(
        lookup_class=lookups.AssessmentLookup, label="Reviewer", required=False
    )

    class Meta:
        model = models.HAWCUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "password1",
            "password2",
            "groups",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id:

            self.fields["password1"].required = False
            self.fields["password2"].required = False

            self.fields["project_manager"].initial = self.instance.assessment_pms.all().values_list(
                "id", flat=True
            )
            self.fields["team_member"].initial = self.instance.assessment_teams.all().values_list(
                "id", flat=True
            )
            self.fields["reviewer"].initial = self.instance.assessment_reviewers.all().values_list(
                "id", flat=True
            )

    def save(self, commit=True):
        user = super().save(commit=commit)
        if user.id:
            user.assessment_pms.set(self.cleaned_data["project_manager"])
            user.assessment_teams.set(self.cleaned_data["team_member"])
            user.assessment_reviewers.set(self.cleaned_data["reviewer"])
        return user
