import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, TemplateView, FormView
from django.views.generic.edit import UpdateView
from django.views.decorators.debug import sensitive_post_parameters

from utils.views import LoginRequiredMixin, MessageMixin

from . import forms
from . import models


def create_account(request):
    """
    Create a new user request. Modified from default such that the username is
    equal to the email address.
    """
    if request.method == 'POST':

        post = request.POST
        form = forms.RegisterForm(post)

        if form.is_valid():
            #create a new user
            user = models.HAWCUser.objects.create_user(post['email'],
                                                       post['password1'])
            user.first_name = post['first_name']
            user.last_name = post['last_name']
            user.full_clean()
            user.save()

            #create a new user profile
            profile = models.UserProfile(user=user)
            profile.save()

            #after save, log user in
            user = authenticate(username=post['email'],
                                password=post['password1'])
            login(request, user)
            return redirect('portal')
    else:
        form = forms.RegisterForm()

    return render(request, 'registration/create_account.html', {'form': form})


class ProfileDetail(LoginRequiredMixin, DetailView):
    model = models.UserProfile

    def get_object(self, **kwargs):
        obj, created = models.UserProfile.objects.get_or_create(user=self.request.user)
        return obj


class ProfileUpdate(LoginRequiredMixin, MessageMixin, UpdateView):
    model = models.UserProfile
    form_class = forms.UserProfileForm
    success_message = 'Profile settings changed.'

    def get_object(self, **kwargs):
        obj, created = models.UserProfile.objects.get_or_create(user=self.request.user)
        return obj


class PasswordChange(LoginRequiredMixin, MessageMixin, UpdateView):
    """
    Prompt the logged-in user for their old password and a new one and change
    the password if the old password is valid.
    """
    template_name = 'myuser/userprofile_form.html'
    success_url = reverse_lazy('user:settings')
    form_class = PasswordChangeForm
    success_message = 'Password changed.'

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(PasswordChange, self).get_form_kwargs()
        kwargs['user'] = kwargs.pop('instance')
        return kwargs

    @method_decorator(sensitive_post_parameters())
    def dispatch(self, request, *args, **kwargs):
        return super(PasswordChange, self).dispatch(request, *args, **kwargs)


class PasswordResetSent(TemplateView):
    template_name = 'registration/password_reset_sent.html'
