from pprint import pformat
from textwrap import dedent

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import REDIRECT_FIELD_NAME, login
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
    RedirectURLMixin,
)
from django.core.mail import mail_admins
from django.forms import ValidationError
from django.http import Http404, HttpRequest, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, DetailView, RedirectView, TemplateView, View
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView

from ...constants import AuthProvider
from ..common.crumbs import Breadcrumb
from ..common.helper import url_query
from ..common.views import LoginRequiredMixin, MessageMixin
from . import forms, models


def get_profile_breadcrumb() -> Breadcrumb:
    return Breadcrumb(name="User profile", url=reverse("user:settings"))


def check_disabled_login(request: HttpRequest) -> HttpResponseRedirect | None:
    hostname = request.get_host()
    if hostname in settings.DISABLED_LOGIN_HOSTS:
        url = reverse("home")
        messages.add_message(
            request,
            level=messages.ERROR,
            message=f"Cannot login on this domain: {hostname}.",
            extra_tags="alert alert-warning",
        )
        return HttpResponseRedirect(url)


class HawcUserCreate(CreateView):
    model = models.HAWCUser
    form_class = forms.RegisterForm
    success_url = reverse_lazy("portal")

    @method_decorator(sensitive_post_parameters("password1", "password2"))
    def dispatch(self, *args, **kwargs):
        # this is redundant with the urls.py, but we can test to confirm it doesn't work
        if settings.HAWC_FEATURES.ANONYMOUS_ACCOUNT_CREATION is False:
            raise Http404()
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return HttpResponseRedirect(self.get_success_url())


class HawcLoginView(LoginView):
    form_class = forms.HAWCAuthenticationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["next_url"] = self.get_redirect_url()
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            next_url = self.get_redirect_url()
            return HttpResponseRedirect(next_url or settings.LOGIN_REDIRECT_URL)
        if settings.AUTH_PROVIDERS == {AuthProvider.external}:
            url = reverse("user:external_auth")
            next_url = self.get_redirect_url()
            if next_url:
                url = url_query(url, {REDIRECT_FIELD_NAME: next_url})
            return HttpResponseRedirect(url)
        if redirect := check_disabled_login(request):
            return redirect
        return super().dispatch(request, *args, **kwargs)


class HawcLogoutView(LogoutView):
    pass


class HawcPasswordResetView(PasswordResetView):
    form_class = forms.HAWCPasswordResetForm
    success_url = reverse_lazy("user:reset_password_sent")


class HawcPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = forms.HAWCSetPasswordForm
    success_url = reverse_lazy("user:password_reset_complete")


class HawcPasswordResetDoneView(PasswordResetDoneView):
    pass


class ProfileDetail(LoginRequiredMixin, DetailView):
    model = models.UserProfile

    def get_object(self, **kwargs):
        obj, created = models.UserProfile.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(self.request.user, "User profile")
        context["token"] = self.request.user.get_api_token()
        return context


class ProfileUpdate(LoginRequiredMixin, MessageMixin, UpdateView):
    model = models.UserProfile
    form_class = forms.UserProfileForm
    success_message = "Profile settings changed."

    def get_object(self, **kwargs):
        obj, created = models.UserProfile.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user, "Update user profile", [get_profile_breadcrumb()]
        )
        return context


class AcceptNewLicense(LoginRequiredMixin, MessageMixin, UpdateView):
    form_class = forms.AcceptNewLicenseForm
    model = models.HAWCUser
    success_message = "License acceptance updated."
    success_url = reverse_lazy("portal")
    template_name = "myuser/accept_license.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        if not settings.ACCEPT_LICENSE_REQUIRED or self.request.user.license_v2_accepted:
            return HttpResponseRedirect(reverse("portal"))
        return super().get(request, *args, **kwargs)


class PasswordChange(LoginRequiredMixin, MessageMixin, UpdateView):
    """
    Prompt the logged-in user for their old password and a new one and change
    the password if the old password is valid.
    """

    template_name = "myuser/userprofile_form.html"
    success_url = reverse_lazy("user:settings")
    form_class = forms.HAWCPasswordChangeForm
    success_message = "Password changed."

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = kwargs.pop("instance")
        return kwargs

    @method_decorator(sensitive_post_parameters())
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = Breadcrumb.build_crumbs(
            self.request.user,
            "Change password",
            [get_profile_breadcrumb()],
        )
        return context


class PasswordResetSent(TemplateView):
    template_name = "registration/password_reset_sent.html"


class SetUserPassword(MessageMixin, UpdateView):
    """
    Manually set HAWCUser password by staff-member.
    """

    model = models.HAWCUser
    template_name = "myuser/set_password.html"
    success_url = reverse_lazy("admin:myuser_hawcuser_changelist")
    form_class = forms.PasswordForm
    success_message = "Password changed."

    @method_decorator(sensitive_post_parameters())
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class PasswordChanged(MessageMixin, RedirectView):
    success_message = "Password changed."

    def get_redirect_url(self):
        self.send_message()
        return reverse_lazy("user:login")


class ExternalAuth(RedirectURLMixin, View):
    def get_user_metadata(self, request) -> dict:
        """
        Retrieve user metadata from request to use for authentication.

        Expected that this request is made from a protected upstream proxy which controls values
        in the incoming request after successful upstream authentication.

        Args:
            request: incoming request

        Returns:
            dict: user metadata; must include "email" and "external_id" keys
        """
        raise NotImplementedError("Deployment specific; requires implementation")

    def mail_bad_headers(self, request):
        """Mail admins when headers don't return valid user metadata"""
        subject = "[External auth]: Bad headers"
        body = f"External authentication failed with the following headers:\n{pformat(request.headers._store)}"
        mail_admins(subject, body)

    def mail_bad_auth(self, email, external_id):
        """Mail admins when the email / external id pair clashes with user in database"""
        subject = "[External auth]: Invalid credentials"
        body = dedent(
            f"""\
            Credentials given in request only partially apply to a user. These credentials are as follows:
            Email: {email}
            External ID: {external_id}
            """
        )
        mail_admins(subject, body)

    def get_redirect_url(self) -> str:
        redirect_to = self.request.GET.get(REDIRECT_FIELD_NAME, "")
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else settings.LOGIN_REDIRECT_URL

    def get(self, request, *args, **kwargs):
        if redirect := check_disabled_login(request):
            return redirect
        # Get user metadata from request
        try:
            metadata = self.get_user_metadata(request)
        except Exception:
            self.mail_bad_headers(request)
            return HttpResponseRedirect(reverse("401"))
        email = metadata.pop("email")
        external_id = metadata.pop("external_id")
        try:
            user = models.HAWCUser.objects.get(email__iexact=email)
            # Save external ID if this is our first access
            if user.external_id is None:
                user.email = email
                user.external_id = external_id
                # Set unusable password if only external auth is allowed
                if settings.AUTH_PROVIDERS == {AuthProvider.external}:
                    user.set_unusable_password()
                user.email = email  # set email case
                user.save()
            # Ensure external id in db matches that returned from service
            elif user.external_id != external_id:
                self.mail_bad_auth(email, external_id)
                return HttpResponseRedirect(reverse("401"))
        except models.HAWCUser.DoesNotExist:
            # Ensure external ID is unique
            if models.HAWCUser.objects.filter(external_id=external_id).exists():
                self.mail_bad_auth(email, external_id)
                return HttpResponseRedirect(reverse("401"))
            # Create user
            user = models.HAWCUser.objects.create_user(
                email=email, external_id=external_id, **metadata
            )
        login(request, user)
        return HttpResponseRedirect(self.get_redirect_url())


class VerifyEmail(MessageMixin, RedirectView):
    url = reverse_lazy("user:login")
    success_message = "Email successfully verified! Ready to login."

    def get_user_or_404(self, uidb64: str) -> models.HAWCUser:
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            return models.HAWCUser.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            models.HAWCUser.DoesNotExist,
            ValidationError,
        ):
            raise Http404()

    def check_token_or_404(self, user: models.HAWCUser, token: str):
        if default_token_generator.check_token(user, token) is False:
            raise Http404()

    def get(self, request, uidb64: str, token: str):
        user = self.get_user_or_404(uidb64)
        self.check_token_or_404(user, token)
        user.set_email_verified()
        self.send_message()
        return super().get(request)


from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.authtoken.models import Token
