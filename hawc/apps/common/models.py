import json
import logging
import math
from enum import IntEnum
from typing import Dict, List, Set, Tuple

import django
import pandas as pd
from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError, connection, models, transaction
from django.db.models import Q, QuerySet, URLField
from django.template.defaultfilters import slugify as default_slugify
from treebeard.mp_tree import MP_Node

from . import forms, validators
from .flavors import help_text as help_text_flavors
from .helper import HAWCDjangoJSONEncoder

_private_storage = FileSystemStorage(location=str(settings.PRIVATE_DATA_ROOT))
logger = logging.getLogger(__name__)


def get_private_data_storage() -> FileSystemStorage:
    return _private_storage


class BaseManager(models.Manager):
    assessment_relation = None

    def _get_order_by(self) -> Tuple[str, ...]:
        """
        We always want a QuerySet to have some sort of defined order when returning. Therefore,
        first try to use the ordering specified by the model. If no ordering exists, order by id.
        """
        ordering = getattr(self.model._meta, "ordering", None)
        return ordering if ordering else ("id",)

    def get_qs(self, assessment_id=None):
        """
        Allows for queryset to be filtered on assessment if assessment_id is passed as argument.
        If assessment_id is not passed, then functions identically to .all()
        """
        ordering = self._get_order_by()
        if assessment_id:
            return self.assessment_qs(assessment_id).order_by(*ordering)
        return self.get_queryset().order_by(*ordering)

    def assessment_qs(self, assessment_id):
        ordering = self._get_order_by()
        return (
            self.get_queryset()
            .filter(Q(**{self.assessment_relation: assessment_id}))
            .order_by(*ordering)
        )

    def valid_ids(self, ids: List[int], **kwargs) -> Set[int]:
        """
        Determines valid model instance ids from a list of ids

        Args:
            ids (List[int]): model instance ids
            kwargs: keyword args to pass to validity check

        Returns:
            Set[int]: A set of all valid ids
        """
        return set(
            self.filter(pk__in=ids, **kwargs)
            .order_by("pk")
            .distinct("pk")
            .values_list("pk", flat=True)
        )

    def invalid_ids(self, ids: List[int], **kwargs) -> Set[int]:
        """
        Determines invalid model instance ids from a list of ids

        Args:
            ids (List[int]): model instance ids
            kwargs: keyword args to pass to validity check

        Returns:
            Set[int]: A set of all invalid ids
        """
        valid_ids = self.valid_ids(ids, **kwargs)
        return set(ids) - valid_ids


class IntChoiceEnum(IntEnum):
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def as_dict(cls) -> Dict:
        return {key.value: key.name for key in cls}


@property
def NotImplementedAttribute(self):
    raise NotImplementedError


class NonUniqueTagBase(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100)
    slug = models.SlugField(verbose_name="Slug", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.pk and not self.slug:
            self.slug = self.slugify(self.name)
            if django.VERSION >= (1, 2):
                from django.db import router

                using = kwargs.get("using") or router.db_for_write(type(self), instance=self)
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
                    res = super().save(*args, **kwargs)
                    transaction.savepoint_commit(sid, **trans_kwargs)
                    return res
                except IntegrityError:
                    transaction.savepoint_rollback(sid, **trans_kwargs)
                    self.slug = self.slugify(self.name, i)
        else:
            return super().save(*args, **kwargs)

    def slugify(self, tag, i=None):
        slug = default_slugify(tag)
        if i is not None:
            slug += f"_{i:d}"
        return slug


class AssessmentRootMixin:

    cache_template_taglist = NotImplementedAttribute
    cache_template_tagtree = NotImplementedAttribute

    @classmethod
    def get_assessment_root_name(cls, assessment_id):
        return f"assessment-{assessment_id}"

    @classmethod
    def get_assessment_root(cls, assessment_id):
        try:
            return cls.objects.get(name=cls.get_assessment_root_name(assessment_id))
        except ObjectDoesNotExist:
            return cls.create_root(assessment_id)

    @classmethod
    def get_assessment_qs(cls, assessment_id, include_root=False):
        root = cls.get_assessment_root(assessment_id)
        if include_root:
            return cls.get_tree(root)
        return root.get_descendants()

    @classmethod
    def annotate_nested_names(cls, qs: QuerySet):
        """
        Include the nested name for each item in the queryset. Assumes the queryset is correctly
        ordered; uses the `name` field and saves to `nested_name` field.

        Args:
            qs (QuerySet): An ordered queryset, like from `get_assessment_qs`
        """
        # preconditions; check that we have a name attribute and we don't have a nested_name attribute
        el = qs.first()
        assert hasattr(el, "name")
        assert not hasattr(el, "nested_name")

        last_depth = -math.inf
        names: List[str] = []
        for node in qs:

            if node.depth == 1:
                node.nested_name = node.name
            else:
                if node.depth > last_depth:
                    pass
                else:
                    for i in range(last_depth - node.depth + 1):
                        names.pop()

                names.append(node.name)
                node.nested_name = "|".join(names)

            last_depth = node.depth

    @classmethod
    def as_dataframe(cls, assessment_id: int, include_root=False) -> pd.DataFrame:
        qs = cls.get_assessment_qs(assessment_id, include_root)
        cls.annotate_nested_names(qs)
        return pd.DataFrame(
            data=[(el.id, el.depth, el.name, el.nested_name) for el in qs],
            columns=["id", "depth", "name", "nested_name"],
        )

    @classmethod
    def assessment_qs(cls, assessment_id):
        include_root = False
        if issubclass(cls, AssessmentRootMixin):
            include_root = True
        ids = (
            cls.get_assessment_qs(assessment_id, include_root)
            .order_by("depth")
            .values_list("id", flat=True)
        )
        ids = list(ids)  # force evaluation
        return cls.objects.filter(id__in=ids)

    @classmethod
    def get_all_tags(cls, assessment_id, json_encode=True):
        """
        Get all tags for the selected assessment.
        """
        key = cls.cache_template_tagtree.format(assessment_id)
        tags = cache.get(key)
        if tags:
            logger.info(f"cache used: {key}")
        else:
            root = cls.get_assessment_root(assessment_id)
            try:
                tags = cls.dump_bulk(root)
            except KeyError as e:
                logger.error(e)
                cls.clean_orphans()
                tags = cls.dump_bulk(root)
                logger.info("ReferenceFilterTag cleanup successful.")
            cache.set(key, tags)
            logger.info(f"cache set: {key}")

        if json_encode:
            return json.dumps(tags, cls=HAWCDjangoJSONEncoder)
        else:
            return tags

    @classmethod
    def clean_orphans(cls):
        """
        Treebeard can sometimes delete parents but retain orphans; this will
        remove all orphans from the tree.
        """
        name = cls.__name__
        logger.warning(f"{name}: attempting to recover...")
        problems = cls.find_problems()
        cls.fix_tree()
        problems = cls.find_problems()
        logger.warning(f"{name}: problems identified: {problems}")
        orphan_ids = problems[2]
        if len(orphan_ids) > 0:
            cursor = connection.cursor()
            for orphan_id in orphan_ids:
                orphan = cls.objects.get(id=orphan_id)
                logger.warning(
                    f'{name} "{orphan.name}" {orphan.id} is orphaned [path={orphan.path}]. Deleting.'
                )
                cursor.execute(
                    f"DELETE FROM {cls._meta.db_table} WHERE id = %s", [orphan.id],
                )
            cursor.close()

    @classmethod
    def get_descendants_pks(cls, assessment_id):
        # Return a list of all descendant ids
        key = cls.cache_template_taglist.format(assessment_id)
        descendants = cache.get(key)
        if descendants:
            logger.info(f"cache used: {key}")
        else:
            root = cls.get_assessment_root(assessment_id)
            descendants = list(root.get_descendants().values_list("pk", flat=True))
            cache.set(key, descendants)
            logger.info(f"cache set: {key}")
        return descendants

    @classmethod
    def clear_cache(cls, assessment_id):
        keys = (
            cls.cache_template_taglist.format(assessment_id),
            cls.cache_template_tagtree.format(assessment_id),
        )
        logger.info(f"removing cache: {', '.join(keys)}")
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
            parent = cls.get_assessment_root(assessment_id)

        # make sure name is valid and not root-like
        if kwargs.get("name") == cls.get_assessment_root_name(assessment_id):
            raise SuspiciousOperation("attempting to create new root")

        # clear cache and create!
        cls.clear_cache(assessment_id)
        return parent.add_child(**kwargs)

    @classmethod
    def create_root(cls, assessment_id, **kwargs):
        """
        Constructor to define root with assessment-creation
        """
        kwargs["name"] = cls.get_assessment_root_name(assessment_id)
        return cls.add_root(**kwargs)

    @classmethod
    def get_maximum_depth(cls, assessment_id):
        # get maximum depth; subtracting root-level
        depth = 0
        descendants = (
            cls.get_assessment_root(assessment_id).get_descendants().values_list("depth", flat=True)
        )
        if descendants:
            depth = max(descendants) - 1
        return depth

    @classmethod
    def validate_and_transform_tag_tree(
        cls, tags_at_level: List[object], issues: List[str], breadcrumbs: List[int] = []
    ):
        """
        Goes through the tags_at_level and for each tag:
            * verifies that it has a name
            * if a slug is present, checks that it's valid. If it's missing, generates one.
            * deletes any keys other than name/slug/children

        Issues found are appended in readable fashion to the issues list; an empty
        issues list indicates that no problems were found. Note that things like a missing slug
        or extraneous keys are NOT reported as issues; they are just corrected in the underlying
        tags data structure.

        This method modifies the supplied tag_tree by relocating the name/data attributes inside a "data" node.

        Args:
            tags_at_level (List[object]): any level of the tag tree
            issues (List[str]): storage for reporting any issues encountered while validating the tree
            breadcrumbs (List[int]): array of indices indicating where in the tree structure the code is at
        """

        def prettify_indices(list_of_indices: List[int]):
            """
            Given a list containing just numeric indices, returns a dot-delimited version with the
            indices wrapped in square brackets.

            For example,
            [8, 6, 7] -> "[8].[6].[7]"

            Args:
                list_of_indices (List[int]): list of indices

            Returns:
                str: formatted string
            """
            return ".".join([f"[{x}]" for x in list_of_indices])

        valid_keys = ["name", "slug", "children"]
        idx = 0
        for tag in tags_at_level:
            tag_name = None
            slug = None
            if "name" in tag:
                tag_name = tag["name"]
                if "slug" in tag:
                    # validate it
                    slug = tag["slug"]
                    recomputed_slug = default_slugify(slug)
                    if recomputed_slug != slug:
                        adjusted_crumbs = prettify_indices(breadcrumbs + [idx])
                        issues.append(
                            f"tag '{tag_name}' at index {adjusted_crumbs} has an invalid slug '{slug}'; should be something like '{default_slugify(tag_name)}' or '{recomputed_slug}'"
                        )
                else:
                    # generate it
                    slug = default_slugify(tag_name)
                    tag["slug"] = slug
            else:
                adjusted_crumbs = prettify_indices(breadcrumbs + [idx])
                issues.append(f"tag at index {adjusted_crumbs} is missing a name")

            # recurse
            if "children" in tag:
                cls.validate_and_transform_tag_tree(tag["children"], issues, breadcrumbs + [idx])

            # delete any extraneous keys that were passed in (could instead/also flag it as an issue?).
            # why not flag an issue? Sometimes it's nice in JSON to change a key to "_oldname" or something,
            # since JSON doesn't support comments. This way we don't break if the caller does something like that.
            keys_to_delete = []
            for key in tag:
                if key not in valid_keys:
                    # need to build up a list; we can't delete from the tag while we iterate through it
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                del tag[key]

            # and now restructure the tag so that name/slug are keys inside a "data" object as Treebeard requires.
            if "name" in tag:
                del tag["name"]
            if "slug" in tag:
                del tag["slug"]
            tag["data"] = {"name": tag_name, "slug": slug}

            idx += 1

    @classmethod
    @transaction.atomic
    def replace_tag_tree_in_assessment(cls, assessment, tag_tree: List[object]):
        """
        Replaces the tag tree for an assessment; this also removes reference/tag associations.

        Args:
            assessment (Assessment): assessment to operate on
            tag_tree (List[object]): the user-supplied tags. This method will create the "assessment-<id>" top parent tag
                                     and should NOT be included in the supplied argument.

        Returns:
            List[dict]: the new complete tag tree, including the "assessment-<id>" top parent tag and all id's
        """
        root_node = cls.get_assessment_root(assessment.id)

        root_name = cls.get_assessment_root_name(assessment.id)
        complete_tree = [{"data": {"name": root_name, "slug": root_name}, "children": tag_tree}]

        root_node.delete()
        cls.load_bulk(complete_tree, parent=None, keep_ids=False)
        cls.clear_cache(assessment.id)
        return cls.get_all_tags(assessment.id, json_encode=False)

    @classmethod
    @transaction.atomic
    def copy_tags(cls, copy_to_assessment, copy_from_assessment) -> Dict[int, int]:
        # delete existing tags for this assessment
        old_root = cls.get_assessment_root(copy_to_assessment.pk)
        old_root.delete()

        # copy tags from alternative assessment, renaming root-tag
        root = cls.get_assessment_root(copy_from_assessment.pk)
        tags = cls.dump_bulk(root)
        assert "name" in tags[0]["data"]
        tags[0]["data"]["name"] = cls.get_assessment_root_name(copy_to_assessment.pk)
        if "slug" in tags[0]["data"]:
            tags[0]["data"]["slug"] = cls.get_assessment_root_name(copy_to_assessment.pk)

        # insert as new taglist
        cls.load_bulk(tags, parent=None, keep_ids=False)
        cls.clear_cache(copy_to_assessment.pk)

        # return mapping of old to new
        def get_tag_ids(taglist: List) -> Tuple[List[int], List[str]]:
            """
            Return a list of tag-ids and tag-names to map from old tag to new tag.
            Args:
                taglist (List): A `dump_bulk` ordered list of tags
            Returns:
                Tuple[List[int], List[str]]: A list of id and name for all tags
            """
            tag_ids = []
            tag_names = []

            def append_child(node):
                # recursively append id and name to lists
                tag_ids.append(node["id"])
                tag_names.append(node["data"]["name"])
                if "children" in node:
                    for child in node["children"]:
                        append_child(child)

            append_child(taglist[0])

            return tag_ids, tag_names

        # return a mapping of old tag id to new tag id
        old_taglist = cls.dump_bulk(cls.get_assessment_root(copy_from_assessment.pk))
        new_taglist = cls.dump_bulk(cls.get_assessment_root(copy_to_assessment.pk))
        old_ids, old_names = get_tag_ids(old_taglist)
        new_ids, new_names = get_tag_ids(new_taglist)
        assert old_names[0] != new_names[0]  # root id should change
        assert old_names[1:] == new_names[1:]  # everything else should be the same
        return {old_id: new_id for old_id, new_id in zip(old_ids, new_ids)}

    def get_assessment_id(self) -> int:
        name = self.name if self.is_root() else self.get_ancestors()[0].name
        return int(name[name.find("-") + 1 :])

    def get_assessment(self):
        try:
            assessment_id = self.get_assessment_id()
            Assessment = apps.get_model("assessment", "Assessment")
            return Assessment.objects.get(id=assessment_id)
        except Exception:
            raise self.__class__.DoesNotExist()

    def moveWithinSiblingsToIndex(self, newIndex):
        siblings = list(self.get_siblings())
        currentPosition = siblings.index(self)

        if currentPosition == newIndex:
            return

        if newIndex == 0:
            self.move(self.get_parent(), pos="first-child")
        else:
            anchor = siblings[newIndex]
            pos = "left" if (newIndex < currentPosition) else "right"
            self.move(anchor, pos=pos)

        self.clear_assessment_cache()

    def clear_assessment_cache(self):
        self.clear_cache(self.get_assessment_id())


class AssessmentRootedTagTree(AssessmentRootMixin, MP_Node):
    """
    MPTT tree, with one root-note for each assessment object in database.
    Implements caching of the tree for quick retrieval. Expects relatively
    small tree for each assessment (<1000 nodes).
    """

    name = models.CharField(max_length=128)

    class Meta:
        abstract = True


class CustomURLField(URLField):
    default_validators = [validators.CustomURLValidator()]

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed
        # twice.
        defaults = {
            "form_class": forms.CustomURLField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)


def get_distinct_charfield(Cls, assessment_id, field):
    return (
        Cls.filter(assessment_id=assessment_id)
        .distinct(field)
        .order_by(field)
        .values_list(field, flat=True)
    )


def get_distinct_charfield_opts(Cls, assessment_id, field):
    objs = get_distinct_charfield(Cls, assessment_id, field)
    return [(obj, obj) for obj in sorted(objs)]


def apply_flavored_help_text(app_name: str):
    """
    Apply custom help-text for specific application flavors; application-specific flavor help text
    are un-tracked migration files.

    Args:
        app_name (str): The application short name
    """
    if not settings.MODIFY_HELP_TEXT:
        return

    # instead of `hawc.apps.animal` use `animal`
    app_name = app_name.split(".")[-1]

    texts = getattr(help_text_flavors, settings.HAWC_FLAVOR, None)
    if texts is None:
        return

    app_config = apps.get_app_config(app_name)
    app_texts = texts.get(app_name)
    for model_name, help_texts in app_texts.items():
        model = app_config.get_model(model_name)
        for field_name, help_text in help_texts.items():
            model._meta.get_field(field_name).help_text = help_text


def get_model_copy_name(instance: models.Model) -> str:
    return getattr(instance, "COPY_NAME", instance._meta.db_table)
