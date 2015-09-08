import json
import logging

import django
from django.db import models, IntegrityError, transaction
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.template.defaultfilters import slugify as default_slugify
from django.utils.translation import ugettext_lazy as _

from treebeard.mp_tree import MP_Node

from utils.helper import HAWCDjangoJSONEncoder


@property
def NotImplementedAttribute(self):
    raise NotImplementedError


def get_crumbs(obj, parent=None):
    if parent is None:
        crumbs = []
    else:
        crumbs = parent.get_crumbs()
    if obj.id is not None:
        crumbs.append((obj.__unicode__(),  obj.get_absolute_url()))
    else:
        crumbs.append((obj._meta.verbose_name.lower(), ))
    return crumbs


class NonUniqueTagBase(models.Model):
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = self.slugify(self.name)
            if django.VERSION >= (1, 2):
                from django.db import router
                using = kwargs.get("using") or router.db_for_write(
                    type(self), instance=self)
                # Make sure we write to the same db for all attempted writes,
                # with a multi-master setup, theoretically we could try to
                # write and rollback on different DBs
                kwargs["using"] = using
                trans_kwargs = {"using": using}
            else:
                trans_kwargs = {}
            i = 0
            while True:
                i += 1
                try:
                    sid = transaction.savepoint(**trans_kwargs)
                    res = super(NonUniqueTagBase, self).save(*args, **kwargs)
                    transaction.savepoint_commit(sid, **trans_kwargs)
                    return res
                except IntegrityError:
                    transaction.savepoint_rollback(sid, **trans_kwargs)
                    self.slug = self.slugify(self.name, i)
        else:
            return super(NonUniqueTagBase, self).save(*args, **kwargs)

    def slugify(self, tag, i=None):
        slug = default_slugify(tag)
        if i is not None:
            slug += "_%d" % i
        return slug


class AssessmentRootedTagTree(MP_Node):
    """
    MPTT tree, with one root-note for each assessment object in database.
    Implements caching of the tree for quick retrieval. Expects relatively
    small tree for each assessment (<1000 nodes).
    """
    name = models.CharField(max_length=128)

    cache_template_taglist = NotImplementedAttribute
    cache_template_tagtree = NotImplementedAttribute

    class Meta:
        abstract = True

    @classmethod
    def get_root_name(cls, assessment_id):
        return 'assessment-{pk}'.format(pk=assessment_id)

    @classmethod
    def get_root(cls, assessment_id):
        try:
            return cls.objects.get(name=cls.get_root_name(assessment_id))
        except ObjectDoesNotExist:
            return cls.create_root(assessment_id)

    @classmethod
    def get_all_tags(cls, assessment_id, json_encode=True):
        """
        Get all tags for the selected assessment.
        """
        key = cls.cache_template_tagtree.format(assessment_id)
        tags = cache.get(key)
        if tags:
            logging.info('cache used: {0}'.format(key))
        else:
            root = cls.get_root(assessment_id)
            tags = cls.dump_bulk(root)
            cache.set(key, tags)
            logging.info('cache set: {0}'.format(key))

        if json_encode:
            return json.dumps(tags, cls=HAWCDjangoJSONEncoder)
        else:
            return tags

    @classmethod
    def get_descendants_pks(cls, assessment_id):
        # Return a list of all descendant ids
        key = cls.cache_template_taglist.format(assessment_id)
        descendants = cache.get(key)
        if descendants:
            logging.info('cache used: {0}'.format(key))
        else:
            root = cls.get_root(assessment_id)
            descendants = list(root.get_descendants().values_list('pk', flat=True))
            cache.set(key, descendants)
            logging.info('cache set: {0}'.format(key))
        return descendants

    @classmethod
    def clear_cache(cls, assessment_id):
        keys = (cls.cache_template_taglist.format(assessment_id),
                cls.cache_template_tagtree.format(assessment_id))
        logging.info('removing cache: {0}'.format(', '.join(keys)))
        cache.delete_many(keys)

    @classmethod
    def create_tag(cls, assessment_id, parent_id=None, **kwargs):
        # get parent
        if parent_id:
            descendants = cls.get_descendants_pks(assessment_id=assessment_id)
            if parent_id not in descendants:
                raise ObjectDoesNotExist("parent_id is not a descendant of assessment_id")
            parent = cls.objects.get(pk=parent_id)
        else:
            parent = cls.get_root(assessment_id)

        # make sure name is valid and not root-like
        if kwargs.get('name') == cls.get_root_name(assessment_id):
            raise SuspiciousOperation("attempting to create new root")

        # clear cache and create!
        cls.clear_cache(assessment_id)
        return parent.add_child(**kwargs)

    @classmethod
    def delete_tag(cls, assessment_id, pk):
        cls.clear_cache(assessment_id)
        cls.objects.filter(pk=pk).delete()

    @classmethod
    def create_root(cls, assessment_id, **kwargs):
        """
        Constructor to define root with assessment-creation
        """
        kwargs["name"] = cls.get_root_name(assessment_id)
        return cls.add_root(**kwargs)

    @classmethod
    def get_maximum_depth(cls, assessment_id):
        # get maximum depth; subtracting root-level
        return max(cls.get_root(assessment_id)
                      .get_descendants()
                      .values_list('depth', flat=True))-1
