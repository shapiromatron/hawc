from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone

from ...constants import AuthProvider
from ..common.models import BaseManager


class UserProfileManager(BaseManager):
    def assessment_qs(self, assessment_id):
        return self.filter(
            models.Q(user__assessment_pms=assessment_id)
            | models.Q(user__assessment_teams=assessment_id)
            | models.Q(user__assessment_reviewers=assessment_id)
        ).distinct()


class HAWCMgr(BaseUserManager):
    # from https://docs.djangoproject.com/en/1.5/topics/auth/customizing/
    # also from UserManager(BaseUserManager)

    def _create_user(self, email, password=None, external_id=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if settings.AUTH_PROVIDERS == {AuthProvider.django} and not password:
            raise ValueError("Users must have a password")
        if settings.AUTH_PROVIDERS == {AuthProvider.external} and not external_id:
            raise ValueError("Users must have an external id")
        if settings.AUTH_PROVIDERS == {AuthProvider.django, AuthProvider.external} and not (
            password or external_id
        ):
            raise ValueError("Users must have a password or external id")

        now = timezone.now()

        user = self.model(
            email=self.normalize_email(email),
            external_id=external_id,
            is_active=True,
            last_login=now,
            date_joined=now,
            **extra_fields,
        )
        user.set_password(password)
        user.save()

        return user

    def create_user(self, email, password=None, external_id=None, **extra_fields):
        extra_fields["is_staff"] = False
        extra_fields["is_superuser"] = False
        return self._create_user(email, password, external_id, **extra_fields)

    def create_superuser(self, email, password=None, external_id=None, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        return self._create_user(email, password, external_id, **extra_fields)

    def active(self):
        return self.filter(is_active=True)
