# Cache class for User Defined Forms.
from hawc.apps.udf.models import ModelUDFContent

from ..common.helper import cacheable


class UDFCache:
    @classmethod
    def _get_model_binding(cls, assessment, model):
        # get UDF model binding for given assessment/model combo
        return assessment.get_model_binding(model)

    @classmethod
    def _get_udf_contents(cls, model_binding, object_id):
        # get saved UDF contents for this object id, if it exists
        try:
            udf_content = model_binding.saved_contents.get(object_id=object_id)
            return udf_content.content
        except ModelUDFContent.DoesNotExist:
            return None

    @classmethod
    def get_model_binding_cache(
        cls,
        assessment,
        model,
        flush: bool = False,
        cache_duration: int = -1,
    ):
        cache_key = f"assessment-{assessment.pk}-{model}-model-binding"
        return cacheable(
            cls._get_model_binding,
            cache_key,
            flush,
            cache_duration,
            assessment=assessment,
            model=model,
        )

    @classmethod
    def get_udf_contents_cache(
        cls,
        model_binding,
        object_id,
        flush: bool = False,
        cache_duration: int = -1,
    ):
        # if this is a new instance, don't bother trying to fetch from the cache
        if object_id is None:
            return None
        cache_key = f"model-binding-{model_binding.pk}-object-{object_id}-udf-contents"
        return cacheable(
            cls._get_udf_contents,
            cache_key,
            flush,
            cache_duration,
            model_binding=model_binding,
            object_id=object_id,
        )

    @classmethod
    def set_udf_contents_cache(cls, model_binding, object_id, content):
        cache_key = f"model-binding-{model_binding.pk}-object-{object_id}-udf-contents"
        return cacheable(lambda content: content, cache_key=cache_key, flush=True, content=content)
