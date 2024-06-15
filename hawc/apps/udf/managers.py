from django.apps import apps
from django.db.models import Manager, Q, QuerySet

from ..common.models import BaseManager


class ModelUDFContentQuerySet(QuerySet):
    def filter_content_type(self, app: str, model: str):
        return self.filter(content_type__app_label=app, content_type__model=model)


class ModelUDFContentManager(BaseManager):
    assessment_relation = "model_binding__assessment"

    def get_queryset(self):
        return ModelUDFContentQuerySet(self.model, using=self._db)


class TagUDFContentQuerySet(QuerySet):
    def filter_tag(self, tag_id: int):
        return self.filter(tag_binding__tag_id=tag_id)

    def consensus_tags_only(self, assessment_id: int):
        TagBinding = apps.get_model("udf", "TagBinding")
        binding_paths = TagBinding.objects.assessment_qs(assessment_id).values_list(
            "tag__path", flat=True
        )
        qs = [self.filter(reference__tags__path__startswith=path) for path in binding_paths]
        # we use unions instead of a Q() because it could be possible that if you use a Q()
        # there could a reference with an unresolved UDF that matches a different UDF
        if len(qs) == 0:
            return self.none()
        elif len(qs) == 1:
            return qs[0]
        else:
            return qs[0].union(*qs[1:])


class TagUDFContentManager(BaseManager):
    assessment_relation = "tag_binding__assessment"

    def get_queryset(self):
        return TagUDFContentQuerySet(self.model, using=self._db)


class ModelBindingManager(BaseManager):
    assessment_relation = "assessment"


class TagBindingManager(BaseManager):
    assessment_relation = "assessment"


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
