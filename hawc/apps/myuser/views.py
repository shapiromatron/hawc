import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView, DetailView, TemplateView, View
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView, UpdateView

from ..common.crumbs import Breadcrumb
from ..common.views import LoginRequiredMixin, MessageMixin
from . import forms, models


def get_profile_breadcrumb() -> Breadcrumb:
    return Breadcrumb(name="User profile", url=reverse("user:settings"))


class HawcUserCreate(CreateView):
    model = models.HAWCUser
    form_class = forms.RegisterForm
    success_url = reverse_lazy("portal")

    @method_decorator(sensitive_post_parameters("password1", "password2"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return HttpResponseRedirect(self.get_success_url())


class HawcLoginView(LoginView):
    form_class = forms.HAWCAuthenticationForm


class HawcLogoutView(LogoutView):
    next_page = reverse_lazy("home")


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


class AcceptNewLicense(MessageMixin, FormView):
    model = models.HAWCUser
    form_class = forms.AcceptNewLicenseForm
    success_message = "License acceptance updated."
    success_url = reverse_lazy("portal")

    def get(self, request, *args, **kwargs):
        return redirect("portal")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


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
            self.request.user, "Change password", [get_profile_breadcrumb()],
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


from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class ExternalAuth(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(
            dict(body=self.request.body.decode("utf-8"), header=self.request.headers._store)
        )

    def post(self, request, *args, **kwargs):
        return JsonResponse(
            dict(body=self.request.body.decode("utf-8"), header=self.request.headers._store)
        )
