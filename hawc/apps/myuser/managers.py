from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone

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

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have an password")

        now = timezone.now()
        user = self.model(
            email=self.normalize_email(email),
            is_staff=False,
            is_active=True,
            is_superuser=False,
            last_login=now,
            date_joined=now,
            **extra_fields,
        )

        user.set_password(password)
        user.save()
        return user

    def create_external_user(self, email, external_id, **extra_fields):
        if not email:
            raise ValueError("External users must have an email address")
        if not external_id:
            raise ValueError("External users must have an IdP id")

        now = timezone.now()
        user = self.model(
            email=self.normalize_email(email),
            external_id=external_id,
            is_staff=False,
            is_active=True,
            is_superuser=False,
            last_login=now,
            date_joined=now,
            **extra_fields,
        )

        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save()
        return u
