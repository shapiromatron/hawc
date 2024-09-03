# Cache class for User Defined Fields.
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.utils import safestring

from ..assessment.models import Assessment
from ..common.helper import cacheable
from .models import ModelBinding


def _get_mb_cache_key(assessment: Assessment, content_type: ContentType):
    return f"assessment-{assessment.id}-udf-model-binding-{content_type.id}"


def _get_model_binding(assessment: Assessment, Model: type[models.Model]):
    return ModelBinding.get_binding(assessment, Model)


class UDFCache:
    @classmethod
    def get_model_binding(
        cls, assessment: Assessment, Model: type[models.Model]
    ) -> ModelBinding | None:
        """Get model binding instance if one exists

        Args:
            assessment (Assessment): assessment instance
            Model (type[models.Model]): the model class

        Returns:
            A ModelBinding instance or None
        """
        ct = ContentType.objects.get_for_model(Model)
        key = _get_mb_cache_key(assessment, ct)
        return cacheable(_get_model_binding, key, assessment=assessment, Model=Model)

    @classmethod
    def clear_model_binding_cache(cls, model_binding: ModelBinding):
        """Clear ModelBinding cache"""
        key = _get_mb_cache_key(model_binding.assessment, model_binding.content_type)
        cache.delete(key)


def _get_tag_cache_key(assessment_id: int) -> str:
    return f"assessment-{assessment_id}-tag-forms"


class TagCache:
    @classmethod
    def get_forms(cls, assessment: Assessment) -> dict[int, safestring.SafeText]:
        key = _get_tag_cache_key(assessment.id)

        def _get_forms(assessment: Assessment) -> dict[int, safestring.SafeText]:
            bindings = assessment.udf_tag_bindings.select_related("form")
            forms = {binding.tag_id: binding.get_form_html() for binding in bindings}
            return forms

        return cacheable(_get_forms, key, assessment=assessment)

    @classmethod
    def clear(cls, assessment_id: int):
        key = _get_tag_cache_key(assessment_id)
        cache.delete(key)
