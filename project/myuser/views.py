from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.views.decorators.debug import sensitive_post_parameters

from django.views.generic.base import RedirectView
from utils.views import LoginRequiredMixin, MessageMixin

from . import forms, models


@sensitive_post_parameters("password1", "password2")
def create_account(request):
    """
    Create a new user request. Modified from default such that the username is
    equal to the email address.
    """
    if request.method == "POST":

        post = request.POST
        form = forms.RegisterForm(post)

        if form.is_valid():
            # use case normalized email
            email = models.HAWCUser.objects.normalize_email(form.cleaned_data["email"])
            pw = form.cleaned_data["password1"]

            # create a new user
            user = models.HAWCUser.objects.create_user(email, pw)
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.license_v2_accepted = form.cleaned_data["license_v2_accepted"]
            user.save()

            # create a new user profile
            models.UserProfile.objects.create(user=user)

            # after save, log user in
            user = authenticate(request, email=form.cleaned_data["email"], password=pw)
            login(request, user)
            return redirect("portal")
    else:
        form = forms.RegisterForm()

    return render(request, "registration/create_account.html", {"form": form})


class ProfileDetail(LoginRequiredMixin, DetailView):
    model = models.UserProfile

    def get_object(self, **kwargs):
        obj, created = models.UserProfile.objects.get_or_create(user=self.request.user)
        return obj


class ProfileUpdate(LoginRequiredMixin, MessageMixin, UpdateView):
    model = models.UserProfile
    form_class = forms.UserProfileForm
    success_message = "Profile settings changed."

    def get_object(self, **kwargs):
        obj, created = models.UserProfile.objects.get_or_create(user=self.request.user)
        return obj


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
