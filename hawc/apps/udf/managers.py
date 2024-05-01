from django.db.models import Manager, Q, QuerySet

from ..common.models import BaseManager


class ModelUDFContentQuerySet(QuerySet):
    def filter_content_type(self, app: str, model: str):
        return self.filter(content_type__app_label=app, content_type__model=model)


class ModelUDFContentManager(BaseManager):
    assessment_relation = "model_binding__assessment"

    def get_queryset(self):
        return ModelUDFContentQuerySet(self.model, using=self._db)


class UserDefinedFormManager(Manager):
    def get_queryset(self):
        return UserDefinedFormQuerySet(self.model, using=self._db)


class UserDefinedFormQuerySet(QuerySet):
    def get_available_udfs(self, user, assessment=None):
        if user.is_staff:
            return self
        return self.filter(
            Q(creator=user)
            | Q(editors=user)
            | Q(published=True)
            | (Q(assessments=assessment) if assessment else Q())
        ).distinct()
