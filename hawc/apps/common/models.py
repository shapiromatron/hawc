import logging
import math
import re
from collections.abc import Iterable, Iterator
from html import unescape

import pandas as pd
from django.apps import apps
from django.conf import settings
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import SearchQuery
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError, connection, models, router, transaction
from django.db.models import Case, CharField, Choices, Q, QuerySet, TextField, URLField, Value, When
from django.db.models.functions import Coalesce, Concat
from django.template.defaultfilters import slugify as default_slugify
from django.utils.html import strip_tags
from treebeard.mp_tree import MP_Node

from . import forms, validators
from .flavors import help_text as help_text_flavors

_private_storage = FileSystemStorage(location=str(settings.PRIVATE_DATA_ROOT))
logger = logging.getLogger(__name__)


def get_private_data_storage() -> FileSystemStorage:
    return _private_storage


class BaseManager(models.Manager):
    assessment_relation = None

    def _get_order_by(self) -> tuple[str, ...]:
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

    def valid_ids(self, ids: list[int], **kwargs) -> set[int]:
        """
        Determines valid model instance ids from a list of ids

        Args:
            ids (list[int]): model instance ids
            kwargs: keyword args to pass to validity check

        Returns:
            set[int]: A set of all valid ids
        """
        return set(
            self.filter(pk__in=ids, **kwargs)
            .order_by("pk")
            .distinct("pk")
            .values_list("pk", flat=True)
        )

    def invalid_ids(self, ids: list[int], **kwargs) -> set[int]:
        """
        Determines invalid model instance ids from a list of ids

        Args:
            ids (list[int]): model instance ids
            kwargs: keyword args to pass to validity check

        Returns:
            set[int]: A set of all invalid ids
        """
        valid_ids = self.valid_ids(ids, **kwargs)
        return set(ids) - valid_ids


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
            using = kwargs.get("using") or router.db_for_write(type(self), instance=self)
            # Make sure we write to the same db for all attempted writes,
            # with a multi-master setup, theoretically we could try to
            # write and rollback on different DBs
            kwargs["using"] = using
            trans_kwargs = {"using": using}
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
            return cls.objects.get(name=cls.get_assessment_root_name(assessment_id), depth=1)
        except ObjectDoesNotExist:
            return cls.create_root(assessment_id)

    @classmethod
    def get_assessment_qs(cls, assessment_id, include_root=False):
        root = cls.get_assessment_root(assessment_id)
        if include_root:
            return cls.get_tree(root)
        return root.get_descendants()

    @classmethod
    def annotate_nested_names(cls, qs: QuerySet) -> QuerySet:
        """
        Include the nested name for each item in the queryset. Assumes the queryset is correctly
        ordered; uses the `name` field and saves to `nested_name` field.

        Args:
            qs (QuerySet): An ordered queryset, like from `get_assessment_qs`
        """

        last_depth = -math.inf
        names: list[str] = []
        for node in qs:
            if node.depth == 1:
                node.nested_name = node.name
            else:
                if node.depth > last_depth:
                    pass
                else:
                    for _i in range(last_depth - node.depth + 1):
                        names.pop()

                names.append(node.name)
                node.nested_name = "|".join(names)

            last_depth = node.depth
        return qs

    @classmethod
    def as_dataframe(cls, assessment_id: int, include_root=False) -> pd.DataFrame:
        qs = cls.get_assessment_qs(assessment_id, include_root)
        cls.annotate_nested_names(qs)
        return pd.DataFrame(
            data=[(el.id, el.depth, el.name, el.nested_name) for el in qs],
            columns=["id", "depth", "name", "nested_name"],
        )

    @classmethod
    def get_all_tags(cls, assessment_id):
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
                    f"DELETE FROM {cls._meta.db_table} WHERE id = %s",  # noqa: S608
                    [orphan.id],
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
        root = cls.get_assessment_root(assessment_id)
        if parent_id is None or parent_id == root.pk:
            parent = root
        else:
            descendants = cls.get_descendants_pks(assessment_id=assessment_id)
            if parent_id not in descendants:
                raise ObjectDoesNotExist("parent_id is not a descendant of assessment_id")
            parent = cls.objects.get(pk=parent_id)

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
    def add_slugs_to_tagtree(cls, tree):
        """Recursively add slugs to a tree if one is missing at any level."""

        def _add_slugs(item):
            if not item["data"].get("slug"):
                item["data"]["slug"] = default_slugify(item["data"]["name"])
            for child in item.get("children", []):
                _add_slugs(child)

        for item in tree:
            _add_slugs(item)

    @classmethod
    @transaction.atomic
    def replace_tree(cls, assessment_id: int, tagtree: list[dict]) -> list[dict]:
        """
        Replaces the tag tree for an assessment; this also removes reference/tag associations.

        Args:
            assessment_id (int): assessment id to operate on
            tagtree (list[dict]): the user-supplied tags. This method will create the "assessment-<id>"
                                    top parent tag and should NOT be included in the supplied argument.

        Returns:
            list[dict]: the new complete tag tree, including the "assessment-<id>" top parent tag and all id's
        """
        cls.add_slugs_to_tagtree(tagtree)

        root_node = cls.get_assessment_root(assessment_id)
        root_name = cls.get_assessment_root_name(assessment_id)
        complete_tree = [{"data": {"name": root_name, "slug": root_name}, "children": tagtree}]

        root_node.delete()
        cls.load_bulk(complete_tree, parent=None, keep_ids=False)
        cls.clear_cache(assessment_id)
        return cls.get_all_tags(assessment_id)

    @classmethod
    @transaction.atomic
    def copy_tags(cls, src_assessment: int, dest_assessment: int) -> dict[int, int]:
        rt = cls.get_assessment_root(src_assessment)
        tree = rt.dump_bulk(rt, keep_ids=True)
        source_tags = tree[0].get("children", [])
        updated_tree = cls.replace_tree(dest_assessment, source_tags)
        return cls.build_tree_mapping(tree, updated_tree)

    @classmethod
    def build_tree_mapping(cls, src: list[dict], dest: list[dict]) -> dict:
        """Map tags IDs from a source tree to destination tree; assumes trees are equal

        Args:
            src (list[dict]): A tree export from dump_bulk
            dest (list[dict]): A tree export from dump_bulk

        Returns:
            dict[int, int]: id key mapping from src to dest
        """
        mapping = {}

        def _match_nodes(_src: list[dict], _dest: list[dict]):
            for idx, src_node in enumerate(_src):
                dest_node = _dest[idx]
                mapping[src_node["id"]] = dest_node["id"]
                if "children" in src_node:
                    _match_nodes(src_node.get("children", []), dest_node.get("children", []))

        _match_nodes(src, dest)
        return mapping

    def get_assessment_id(self) -> int:
        name = self.name if self.is_root() else self.get_ancestors()[0].name
        return int(name[name.find("-") + 1 :])

    def get_assessment(self):
        try:
            assessment_id = self.get_assessment_id()
            Assessment = apps.get_model("assessment", "Assessment")
            return Assessment.objects.get(id=assessment_id)
        except Exception as exc:
            raise self.__class__.DoesNotExist() from exc

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
    return [(obj, obj) for obj in sorted(objs) if obj]


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


def include_related(
    queryset: QuerySet, ancestors: bool = True, descendants: bool = True
) -> QuerySet:
    """Update treebeard.MP_Node QuerySet to include related objects.

    Args:
        queryset (QuerySet): A treebeard.MP_Node QuerySet
        ancestors (bool, optional): Include direct ancestors of items in QuerySet
        descendants (bool, optional): Include descendants of items in QuerySet

    Returns:
        A QuerySet containing items from the original queryset and any additional items
    """
    if not ancestors and not descendants:
        return queryset

    paths = list(queryset.values_list("path", "depth"))
    if len(paths) == 0:
        return queryset

    filters = Q()
    steplen = queryset.model.steplen
    if ancestors:
        parent_paths = []
        for path, depth in paths:
            for d in range(depth - 1):
                parent_paths.append(path[: ((d + 1) * steplen)])
        filters |= Q(path__in=parent_paths)

    if descendants:
        items = "|".join(p for p, _ in paths)
        filters |= Q(path__regex=f"^({items}).+")

    return queryset | queryset.model.objects.filter(filters)


def sql_display(name: str, choice: type[Choices] | dict, default="?") -> Case:
    """Create an annotation to return the display name via SQL

    Args:
        name (str): the field name
        choice (type[Choices]): a choice field or dict of choices
        default: default value if display value is not found

    Returns:
        Case: the case statement for use in an annotation
    """
    choices = choice.items() if isinstance(choice, dict) else choice.choices
    return Case(
        *(When(**{name: key, "then": Value(value)}) for key, value in choices),
        default=Value(default),
    )


def sql_format(format_str: str, *field_params) -> Concat:
    """Create an ORM expression to simulate a format string.

    Args:
        format_str (str): Format string. Any {} present in the string
        will be replaced by field_params.

    Returns:
        Concat: An expression that generates a string
    """
    value_params = format_str.split("{}")
    if format_str.count("{}") != len(field_params):
        raise ValueError("field params must be equal to value params.")
    replace_num = len(field_params)
    concat_args = []
    for i in range(replace_num):
        if value_params[i]:
            concat_args.append(Value(value_params[i]))
        concat_args.append(field_params[i])
    if remainder := "".join(value_params[replace_num:]):
        concat_args.append(Value(remainder))
    return Concat(*concat_args, output_field=TextField())


def replace_null(field: str, replacement: str = ""):
    """Replace null values with a replacement string

    Args:
        field (str): The field to replace
        replacement (str, optional): The replacement string. Defaults to "".
    """
    return Coalesce(field, Value(replacement), output_field=CharField())


def str_m2m(field: str, delimiter: str = "|", default: str = "", **kw):
    """Generate a delimited string aggregation of a m2m field.

    The resulting aggregation must be saved to an annotation on the QuerySet;
    you cannot use directly on a values_list (but you can use after annotation).

    Args:
        field (str): The field name to aggregate
        delimiter (str, optional): The field to use; defaults to "|".
        default (str, optional): The default value to use; defaults to "".
    """
    return StringAgg(field, delimiter=delimiter, distinct=True, default=Value(default), **kw)


def to_display(series: pd.Series, Choice: type[Choices]) -> pd.Series:
    """Return a new series of display values from django choices

    Args:
        series (pd.Series): the series with db values
        Choice (type[Choices]): a Choices instance

    Returns:
        pd.Series: a series of display values
    """
    return series.map({k: v for k, v in Choice.choices}).fillna("?")


def to_display_array(series: pd.Series, Choice: type[Choices], delimiter: str = "|") -> pd.Series:
    """Return a new series of delimited display values from django choices

    Args:
        series (pd.Series): the series with db values
        Choice (type[Choices]): a Choices instance
        delimiter (str, optional): delimiter to use. Defaults to "|".

    Returns:
        pd.Series: a series of delimited display values
    """
    mapping = {k: v for k, v in Choice.choices}
    return (
        series.str.split(pat=delimiter)
        .apply(lambda items: [mapping.get(item, "?") for item in items])
        .str.join(delimiter)
    )


def pd_strip_tags(df: pd.DataFrame, columns: list[str]):
    """Remove tags from text columns a DataFrame; in place

    Args:
        df (pd.DataFrame): the DataFrame to clean
        columns (list[str]): column names to remove tags
    """
    for col in columns:
        df.loc[:, col] = df[col].apply(lambda txt: unescape(strip_tags(txt)))


class NumericTextField(models.CharField):
    generic_help_text = "Non-numeric values can be used if necessary, but should be limited to <, ≤, ≥, >, LOD, LOQ."
    validators = [validators.NumericTextValidator()]


def clone_name(instance: models.Model, field: str) -> str:
    # Get a valid clone name for an instance of a model, that's under the required char size limit.
    value = getattr(instance, field)
    max_length = instance._meta.get_field(field).max_length
    text = value
    new_suffix = " (2)"
    if m := re.search(r" \((\d+)\)$", value):
        text = value[: -len(m[0])]
        new_suffix = f" ({int(m[1]) + 1})"
    return text[: max_length - len(new_suffix)] + new_suffix


def sql_query_to_dicts(sql: str, params: Iterable | None = None) -> Iterator[dict]:
    """Return a list of dictionaries from a SQL SELECT statement.

    Args:
        sql (str): A SQL query; must start with SELECT
        params (Iterable | None, optional): Parameters for the query; defaults to None.

    Yields:
        Iterator[dict]: an iterator of dictionaries
    """
    if sql.upper().startswith("SELECT") is False:
        raise ValueError("Query must start with SELECT")
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        yield from (dict(zip(columns, row, strict=True)) for row in cursor.fetchall())


class ColorField(models.CharField):
    default_validators = [validators.ColorValidator()]

    def formfield(self, **kwargs):
        return super().formfield(
            **{
                "form_class": forms.ColorField,
                **kwargs,
            }
        )


def search_query(value: str) -> SearchQuery:
    return SearchQuery(value, search_type="websearch", config="english")

