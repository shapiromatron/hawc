from django.db.models import QuerySet

from ..common.models import BaseManager


class ModelUDFContentQuerySet(QuerySet):
    def filter_content_type(self, app: str, model: str):
        return self.filter(content_type__app_label=app, content_type__model=model)


class ModelUDFContentManager(BaseManager):
    assessment_relation = "model_binding__assessment"

    def get_queryset(self):
        return ModelUDFContentQuerySet(self.model, using=self._db)
