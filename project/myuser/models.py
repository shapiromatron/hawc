from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


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


class HAWCUser(AbstractBaseUser, PermissionsMixin):
    objects = HAWCMgr()
    email = models.EmailField(verbose_name="Email address (username)",
                              max_length=254, unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'


    class Meta:
        ordering = ("last_name", )

    def __unicode__(self):
        return self.get_full_name()

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.username)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])


class UserProfile(models.Model):
    user = models.OneToOneField(HAWCUser, related_name='profile')
    HERO_access = models.BooleanField(default=False,
        verbose_name='HERO access',
        help_text='All HERO links will redirect to the login-only HERO access ' + \
                  'page, allowing for full article text.'
    )

    def __unicode__(self):
        return self.user.get_full_name() + ' Profile'

    def get_absolute_url(self):
        return reverse('user:settings')

    def get_assessment(self):
        return self.assessment
