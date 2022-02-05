from base64 import b64encode
from io import BytesIO

import pyotp
import qrcode
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token

from ..common.helper import SerializerHelper
from . import managers


class HAWCUser(AbstractBaseUser, PermissionsMixin):

    objects = managers.HAWCMgr()

    email = models.EmailField(max_length=254, unique=True, db_index=True)
    first_name = models.CharField("first name", max_length=30, blank=True)
    last_name = models.CharField("last name", max_length=30, blank=True)
    external_id = models.CharField(max_length=30, unique=True, blank=True, null=True, default=None)
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into this admin " "site.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as "
        "active. Unselect this instead of deleting accounts.",
    )
    license_v1_accepted = models.BooleanField(default=False, verbose_name="Accept license")
    license_v2_accepted = models.BooleanField(default=False, verbose_name="Accept license")
    otp_secret = models.CharField(max_length=32)
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    USERNAME_FIELD = "email"
    CAN_CREATE_ASSESSMENTS = "can-create-assessments"

    class Meta:
        ordering = ("last_name",)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_assessments(self):
        Assessment = apps.get_model("assessment", "Assessment")
        return Assessment.objects.get_viewable_assessments(self)

    def get_json(self, json_encode=True):
        return SerializerHelper.get_serialized(self, json=json_encode)

    def send_welcome_email(self):
        subject = "Welcome to HAWC!"
        context = dict(
            user=self, assessments=self.get_assessments(), domain=Site.objects.get_current().domain
        )

        plaintext = render_to_string("myuser/welcome_email.txt", context)
        html = render_to_string("myuser/welcome_email.html", context)

        msg = EmailMultiAlternatives(subject, plaintext, None, [self.email])
        msg.attach_alternative(html, "text/html")
        msg.send()

    def create_profile(self) -> "UserProfile":
        authenticated_hero = True if "@epa.gov" in self.email else False
        return UserProfile.objects.create(user=self, authenticated_hero=authenticated_hero)

    def is_beta_tester(self):
        return self.is_staff or self.groups.filter(name="beta tester").exists()

    def can_create_assessments(self):
        if settings.ANYONE_CAN_CREATE_ASSESSMENTS:
            return True
        else:
            return (
                self.is_superuser or self.groups.filter(name=self.CAN_CREATE_ASSESSMENTS).exists()
            )

    def get_api_token(self) -> Token:
        token, _ = Token.objects.get_or_create(user=self)
        return token

    def destroy_api_token(self):
        Token.objects.filter(user=self).delete()

    @property
    def otp_enabled(self) -> bool:
        return len(self.otp_secret) > 0

    def _get_2fa(self) -> pyotp.TOTP:
        issuer = settings.ALLOWED_HOSTS[0] if len(settings.ALLOWED_HOSTS) > 0 else "hawc"
        return pyotp.TOTP(self.otp_secret, name=self.email, issuer=issuer)

    def set_2fa_token(self):
        self.otp_secret = pyotp.random_base32()

    def check_2fa_token(self, token: str) -> bool:
        return self._get_2fa().verify(token)

    def get_2fa_image(self):
        """
        Generate a QR code from user's TOTP session; return a base-64 encoded html html img tag.
        """
        f = BytesIO()
        img = qrcode.make(self._get_2fa().provisioning_uri())
        img.save(f, format="png")
        data = b64encode(f.getvalue()).decode("utf-8")
        return f'<img width="150px" src="data:image/png;base64,{data}" alt="Two factor QR code">'


class UserProfile(models.Model):
    objects = managers.UserProfileManager()

    user = models.OneToOneField(HAWCUser, on_delete=models.CASCADE, related_name="profile")
    authenticated_hero = models.BooleanField(
        default=False,
        verbose_name="Authenticated HERO access",
        help_text="Use the login-required version of HERO links, instead of the public version",
    )

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

    def get_absolute_url(self):
        return reverse("user:settings")
