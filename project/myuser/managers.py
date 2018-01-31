from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth import login
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone

from utils.models import BaseManager


class UserProfileManager(BaseManager):

    def assessment_qs(self, assessment_id):
        return self.filter(
                models.Q(user__assessment_pms=assessment_id) |
                models.Q(user__assessment_teams=assessment_id) |
                models.Q(user__assessment_reviewers=assessment_id)
            ).distinct()

class HAWCMgr(BaseUserManager):
    # from https://docs.djangoproject.com/en/1.5/topics/auth/customizing/
    # also from UserManager(BaseUserManager)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have an password')

        now = timezone.now()
        user = self.model(email=self.normalize_email(email),
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)

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

    def create_user_batch(self, email, first_name, last_name,
                         pms=False, tms=False, rvs=False,
                         welcome_email=False):
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
            last_name=last_name)

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
                models.Q(assessment_pms=assessment_id) |
                models.Q(assessment_teams=assessment_id) |
                models.Q(assessment_reviewers=assessment_id)
            ).distinct()

    def lookup_by_epa_sso_uid(self, httpRequest):
        """
        Attempts to instantiate this HAWCUser object by using an incoming EPA single-sign-on User ID
        This method does not return anything, but instead sets the incoming httpRequest object's user attribute to the user found
        from the value found in the request's "UID" header field
        """

        if ((isinstance(httpRequest, WSGIRequest)) and (httpRequest.user.is_anonymous)):
            # The incoming httpRequest argument is of the expected type, continue checking
            keyName = "HTTP_UID"

            if ((keyName in httpRequest.META) and (isinstance(httpRequest.META[keyName], str)) and (httpRequest.META[keyName] != "")):
                # httpRequest has a non-empty "HTTP_UID" request header, use it to look up the HAWCUser in the database

                userSet = self.filter(models.Q(epa_sso_uid=httpRequest.META[keyName]))
                if (len(userSet) >= 1):
                    # At least one user was found with that EPA Single-Sign-On UserID, take the first one and use it as request.user
                    login(httpRequest, userSet[0])
