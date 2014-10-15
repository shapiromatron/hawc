from taggit.utils import require_instance_manager
from taggit.managers import TaggableManager, _TaggableManager


class ReferenceFilterTagManager(TaggableManager):

    def __get__(self, instance, model):
        if instance is not None and instance.pk is None:
            raise ValueError("%s objects need to have a primary key value "
                "before you can access their tags." % model.__name__)
        manager = _ReferenceFilterTagManager(
            through=self.through,
            model=model,
            instance=instance,
            prefetch_cache_name = self.name
        )
        return manager


class _ReferenceFilterTagManager(_TaggableManager):

    @require_instance_manager
    def set(self, tag_pks):
        # optimized to reduce queries
        self.clear()

        # make sure we're only using pks for tags with this assessment
        tag_pks = [int(tag) for tag in tag_pks]
        full_taglist = self.through.tag_model().get_descendants_pks(self.instance.assessment_id)
        selected_tags = set(tag_pks).intersection(full_taglist)

        tagrefs = []
        for tag_id in selected_tags:
            tagrefs.append(self.through(tag_id=tag_id, content_object=self.instance))
        self.through.objects.bulk_create(tagrefs)
