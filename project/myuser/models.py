from django.apps import apps
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.sites.models import Site
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template.loader import render_to_string
from django.template import Context

from utils.helper import SerializerHelper
from . import managers


class HAWCUser(AbstractBaseUser, PermissionsMixin):
    objects = managers.HAWCMgr()
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    license_v1_accepted = models.BooleanField(default=False)
    license_v2_accepted = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ("last_name", )

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_assessments(self):
        Assessment = apps.get_model('assessment', 'Assessment')
        return Assessment.objects.get_viewable_assessments(self)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def send_welcome_email(self):
        subject = "Welcome to HAWC!"
        context = Context(dict(
            user=self,
            assessments=self.get_assessments(),
            domain=Site.objects.get_current().domain,
        ))

        plaintext = render_to_string('myuser/welcome_email.txt', context)
        html = render_to_string('myuser/welcome_email.html', context)

        msg = EmailMultiAlternatives(subject, plaintext, None, [self.email])
        msg.attach_alternative(html, "text/html")
        msg.send()


class UserProfile(models.Model):
    objects = managers.UserProfileManager()

    user = models.OneToOneField(HAWCUser, related_name='profile')
    HERO_access = models.BooleanField(
        default=False,
        verbose_name='HERO access',
        help_text='All HERO links will redirect to the login-only HERO access '
                  'page, allowing for full article text.')

    def __str__(self):
        return self.user.get_full_name() + ' Profile'

    def get_absolute_url(self):
        return reverse('user:settings')

    def get_assessment(self):
        return self.assessment
