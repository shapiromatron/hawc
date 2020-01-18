from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
from django.utils import timezone

from utils.models import BaseManager


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

    def create_superuser(self, email, password=None, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save()
        return u

    def create_user_batch(
        self, email, first_name, last_name, pms=False, tms=False, rvs=False, welcome_email=False,
    ):
        """
        Create a HAWC user, assign to assessments, and optionally send a welcome-email.
        Used for batch-creation of multiple users by administrators.

        Assessment-are a list of assessment-ids or False if none are added.

        Example method call:

            create_hawc_user("hikingfan@gmail.com", "George", "Washington",
                             pms=[1,2,3] tms=False, rvs=False,
                             welcome_email=True)
        """
        user = self.create_user(
            email=email,
            password=self.make_random_password(),
            first_name=first_name,
            last_name=last_name,
        )

        if pms:
            user.assessment_pms.add(*pms)

        if tms:
            user.assessment_teams.add(*tms)

        if rvs:
            user.assessment_reviewers.add(*rvs)

        if welcome_email:
            user.send_welcome_email()

    def assessment_qs(self, assessment_id):
        return self.filter(
            models.Q(assessment_pms=assessment_id)
            | models.Q(assessment_teams=assessment_id)
            | models.Q(assessment_reviewers=assessment_id)
        ).distinct()
