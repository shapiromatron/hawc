# Cache class for User Defined Forms.
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models

from ..assessment.models import Assessment
from ..common.helper import cacheable
from .models import ModelBinding


def _get_cache_key(assessment: Assessment, content_type: ContentType):
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
        key = _get_cache_key(assessment, ct)
        return cacheable(_get_model_binding, key, assessment=assessment, Model=Model)

    @classmethod
    def clear_model_binding_cache(cls, model_binding: ModelBinding):
        """Clear ModelBinding cache"""
        key = _get_cache_key(model_binding.assessment, model_binding.content_type)
        cache.delete(key)
