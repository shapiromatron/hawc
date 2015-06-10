from django import forms
from django.forms import ModelForm
from django.contrib.auth import get_backends
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm

from selectable.forms import AutoCompleteSelectMultipleField

from assessment import lookups

from . import models


_PASSWORD_HELP = ('Password must be at least eight characters in length, ' +
                  'at least one special character, and at least one digit.')


def checkPasswordComplexity(pw):
    special_characters = r"""~!@#$%^&*()_-+=[]{};:'"\|,<.>/?"""
    if (
        (len(pw) < 8) or
        (not any(char.isdigit() for char in pw)) or
        (not any(char in special_characters for char in pw))
    ):
        raise forms.ValidationError(_PASSWORD_HELP)


class PasswordForm(forms.ModelForm):

    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput,
                                help_text=_PASSWORD_HELP)
    password2 = forms.CharField(label='Password confirmation',
                                widget=forms.PasswordInput)

    class Meta:
        model = models.HAWCUser
        fields = ("password1", "password2")

    def clean_password1(self):
        pw = self.cleaned_data['password1']
        if not self.fields['password1'].required and pw == "":
            return pw
        checkPasswordComplexity(pw)
        return pw

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if not self.fields['password2'].required and password2 == "":
            return password2
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(PasswordForm, self).save(commit=False)
        if self.cleaned_data["password1"] != "":
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class RegisterForm(PasswordForm):
    _accept_license_help_text = "License must be accepted in order to create an account."

    accept_license = forms.BooleanField(
        label="Accept License",
        required=False,
        help_text=_accept_license_help_text)

    class Meta:
        model = models.HAWCUser
        fields = ("email", "first_name", "last_name",
                  "password1", "password2")

    def clean_accept_license(self):
        if not self.cleaned_data['accept_license']:
            raise forms.ValidationError(self._accept_license_help_text)


class UserProfileForm(ModelForm):

    first_name = forms.CharField(label="First name", required=True)
    last_name = forms.CharField(label="Last name", required=True)

    class Meta:
        model = models.UserProfile
        fields = ("first_name", "last_name", "HERO_access")

    def save(self, commit=True):
        # save content to both UserProfile and User
        up = super(UserProfileForm, self).save(commit=False)
        up.user.first_name = self.cleaned_data["first_name"]
        up.user.last_name = self.cleaned_data['last_name']
        if commit:
            up.save()
            up.user.save()
        return up


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
            user.backend = "%s.%s" % (backend.__module__,
                                      backend.__class__.__name__)
            return user
        else:
            return None
    except models.HAWCUser.DoesNotExist:
        return None


class HAWCAuthenticationForm(AuthenticationForm):
    """
    Modified to do a case-insensitive comparison of emails.
    """
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = hawc_authenticate(email=username,
                                                password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'] % {
                        'username': self.username_field.verbose_name
                    })
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        return self.cleaned_data


class HAWCPasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super(HAWCPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].help_text = "Email-addresses are case-sensitive."

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            models.HAWCUser.objects.get(email=email)
        except models.HAWCUser.DoesNotExist:
            raise forms.ValidationError("Email address not found")

        return email


class AdminUserForm(PasswordForm):

    project_manager = AutoCompleteSelectMultipleField(
        lookup_class=lookups.AssessmentLookup,
        label='Project manager',
        required=False)
    team_member = AutoCompleteSelectMultipleField(
        lookup_class=lookups.AssessmentLookup,
        label='Team member',
        required=False)
    reviewer = AutoCompleteSelectMultipleField(
        lookup_class=lookups.AssessmentLookup,
        label='Reviewer',
        required=False)

    class Meta:
        model = models.HAWCUser
        fields = ("email", "first_name", "last_name",
                  "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(AdminUserForm, self).__init__(*args, **kwargs)
        if self.instance.id:

            self.fields['password1'].required = False
            self.fields['password2'].required = False

            self.fields['project_manager'].initial = self.instance\
                .assessment_pms.all()\
                .values_list('id', flat=True)
            self.fields['team_member'].initial = self.instance\
                .assessment_teams.all()\
                .values_list('id', flat=True)
            self.fields['reviewer'].initial = self.instance\
                .assessment_reviewers.all()\
                .values_list('id', flat=True)

    def save(self, commit=True):
        user = super(AdminUserForm, self).save(commit=commit)
        if user.id:
            user.assessment_pms.add(*self.cleaned_data['project_manager'])
            user.assessment_teams.add(*self.cleaned_data['team_member'])
            user.assessment_reviewers.add(*self.cleaned_data['reviewer'])
        return user
