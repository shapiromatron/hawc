# Cache class for User Defined Forms.
from django.core.cache import cache

from hawc.apps.udf.models import ModelUDFContent

from ..common.helper import cacheable


class UDFCache:
    @classmethod
    def get_model_binding_cache(
        cls,
        assessment,
        model,
        flush: bool = False,
        cache_duration: int = -1,
    ):
        def _get_model_binding(assessment, model):
            # get UDF model binding for given assessment/model combo
            return assessment.get_model_binding(model)

        cache_key = f"assessment-{assessment.pk}-{model}-model-binding"
        return cacheable(
            _get_model_binding,
            cache_key,
            flush,
            cache_duration,
            assessment=assessment,
            model=model,
        )

    @classmethod
    def clear_model_binding_cache(cls, model_binding):
        cache_key = f"assessment-{model_binding.assessment_id}-{model_binding.content_type.model}-model-binding"
        cache.delete(cache_key)

    @classmethod
    def get_udf_contents_cache(
        cls,
        model_binding,
        object_id,
        flush: bool = False,
        cache_duration: int = -1,
    ):
        def _get_udf_contents(model_binding, object_id):
            # get saved UDF contents for this object id, if it exists
            try:
                udf_content = model_binding.saved_contents.get(object_id=object_id)
                return udf_content.content
            except ModelUDFContent.DoesNotExist:
                return None

        # if this is a new instance, don't bother trying to fetch from the cache
        if object_id is None:
            return None
        cache_key = f"model-binding-{model_binding.pk}-object-{object_id}-udf-contents"
        return cacheable(
            _get_udf_contents,
            cache_key,
            flush,
            cache_duration,
            model_binding=model_binding,
            object_id=object_id,
        )

    @classmethod
    def set_udf_contents_cache(
        cls,
        udf_content: ModelUDFContent,
        cache_duration: int = -1,
    ):
        cache_key = f"model-binding-{udf_content.model_binding_id}-object-{udf_content.object_id}-udf-contents"
        return cacheable(
            lambda c: c, cache_key, flush=True, cache_duration=cache_duration, c=udf_content.content
        )
