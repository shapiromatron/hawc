from django.db import models


class UserDefinedFormManager(models.Manager):
    def get_queryset(self):
        return UserDefinedFormQuerySet(self.model, using=self._db)


class UserDefinedFormQuerySet(models.QuerySet):
    def get_available_udfs(self, user, assessment=None):
        if user.is_staff:
            return self
        return self.filter(
            models.Q(creator=user)
            | models.Q(editors=user)
            | models.Q(published=True)
            | (models.Q(assessments=assessment) if assessment else models.Q())
        ).distinct()
