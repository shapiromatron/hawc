import decimal
import logging
import re
from collections import defaultdict
from collections.abc import Callable, Iterable
from datetime import timedelta
from itertools import chain
from math import inf
from typing import Any, NamedTuple, TypeVar

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Choices, QuerySet
from django.http import HttpRequest, QueryDict
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.functional import lazy
from django.utils.html import strip_tags
from django.utils.http import urlencode
from docx.document import Document
from matplotlib.axes import Axes
from matplotlib.dates import DateFormatter
from pydantic import BaseModel as PydanticModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.serializers import ValidationError as DRFValidationError

from .middleware import _local_thread

logger = logging.getLogger(__name__)


def rename_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename column headers inplace to ensure no header names are duplicated.

    Args:
        df (pd.DataFrame): A dataframe with a single index of columns

    Returns:
        pd.DataFrame: The dataframe with headers renamed; inplace
    """
    if not df.columns.has_duplicates:
        return df
    duplicates: set[str] = set(df.columns[df.columns.duplicated()].tolist())
    indexes: dict[str, int] = defaultdict(lambda: 0)
    new_cols: list[str] = []
    for col in df.columns:
        if col in duplicates:
            indexes[col] += 1
            new_cols.append(f"{col}.{indexes[col]}")
        else:
            new_cols.append(col)
    df.columns = new_cols
    return df


def HAWCtoDateString(datetime):
    """
    Helper function to ensure dates are consistent.
    """
    return datetime.strftime("%B %d %Y, %I:%M %p")


def cleanHTML(txt: str):
    return strip_entities(
        strip_tags(
            txt.replace("\n", " ").replace("\r", "").replace("<br>", "\n").replace("&nbsp;", " ")
        )
    )


def strip_entities(value):
    """Return the given HTML with all entities (&something;) stripped."""
    # Note: Originally in Django but removed in v1.10
    return re.sub(r"&(?:\w+|#\d+);", "", force_str(value))


def tryParseInt(
    value: Any, default: int | None = None, min_value: int = -inf, max_value: int = inf
) -> int | None:
    """Cast value to integer if possible, or return None

    Args:
        value (Any): the value to cast
        default (int, optional): default value if cannot be cast; defaults to None
        min_value (int, optional): minimum acceptable value; defaults to -inf
        max_value (int, optional): maximum acceptable value; defaults to inf

    Returns:
        Optional[int]: An integer or None
    """
    try:
        return min(max_value, max(min_value, int(value)))
    except (ValueError, TypeError):
        return default


def try_parse_list_ints(val: str | None = None) -> list[int]:
    """
    Try to parse a list of integers and return a list of integers, eg., `1,2,3` -> [1,2,3].
    If this fails for any reason, an empty list is returned
    """
    if val is None:
        return []
    try:
        return [int(item) for item in val.split(",")]
    except ValueError:
        return []


def int_or_float(val: float) -> int | float:
    """
    Tries to cast val to int without loss.
    If unable to, it returns the original float.
    """
    return int(val) if int(val) == val else val


def map_enum(df: pd.DataFrame, field: str, choices: Choices, replace: bool = False):
    """Add new column inplace in dataframe with enum text display versions of a field.

    Args:
        df (pd.DataFrame): The input/output dataframe
        field (str): The field with the enum
        choices (Choices): The field to map
        replace (bool, default False): If True, replaces the current field. If false, adds a
            "_display" suffix to the end of the field name and create a new field

    """
    key = f"{field}_display"
    mapping = {key: value for (key, value) in choices.choices}
    df.loc[:, key] = df[field].map(mapping)
    df.insert(df.columns.get_loc(field) + 1, key, df.pop(key))
    if replace:
        df.pop(field)
        df.rename(columns={key: field}, inplace=True)


def reorder_list(items: list, target: Any, after: Any | None = None, n_cols: int = 1) -> list:
    """Returns a copy of a list with elements reordered.

    Args:
        items (list): a list of items
        target (Any): the key to move
        after (Any | None, default None): the key to move target after.
        n_cols (int, default 1): the number of sequential targets to move.

    Raises:
        NotImplementedError: _description_

    Returns:
        list: _description_
    """
    target_index = items.index(target)
    target_index_max = target_index + n_cols
    insert_index = (-1 if after is None else items.index(after)) + 1

    if target_index == insert_index:
        return items
    elif target_index > (insert_index):
        return (
            items[:insert_index]
            + items[target_index:target_index_max]
            + items[insert_index:target_index]
            + items[target_index_max:]
        )
    elif target_index_max < insert_index:
        return (
            items[:target_index]
            + items[target_index_max:insert_index]
            + items[target_index:target_index_max]
            + items[insert_index:]
        )
    else:
        raise NotImplementedError("Unreachable code")


def df_move_column(
    df: pd.DataFrame, target: str, after: str | None = None, n_cols: int = 1
) -> pd.DataFrame:
    """Move target column after another column.

    Args:
        df (pd.DataFrame): The dataframe to modify.
        target (str): Name of the column to move
        after (Optional[str], optional): Name of column to move after; if None, puts first
        n_cols (int): Number of target columns to move; defaults to 1

    Returns:
        pd.DataFrame: The mutated dataframe.
    """
    new_cols = reorder_list(df.columns.tolist(), target, after, n_cols)
    return df[new_cols]


def url_query(path: str, query: dict) -> str:
    """Generate a URL with appropriate query string parameters

    Args:
        path (str): The url path
        query (dict): A dictionary of parameters to add

    Returns:
        str: A url-encoded string with query values
    """
    if not query:
        return path
    q = QueryDict("", mutable=True)
    q.update(query)
    return f"{path}?{q.urlencode()}"


def new_window_a(href: str, text: str) -> str:
    # assumes href and text are safe strings
    return f'<a rel="noopener noreferrer" target="_blank" href="{href}">{text}</a>'


class HAWCDjangoJSONEncoder(DjangoJSONEncoder):
    """
    Modified to return a float instead of a string.
    """

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        else:
            return super().default(o)


class SerializerHelper:
    """
    HAWC helper-object for getting serialized objects and setting cache.
    Sets cache names based on django models and primary keys automatically.
    Sets a cache using the serialized object, and also a JSON object.
    """

    serializers = {}

    @classmethod
    def _get_cache_name(cls, model, id, json=True):
        name = f"{model.__module__}.{model.__name__}.{id}"
        if json:
            name += ".json"
        return name

    @classmethod
    def get_serialized(cls, obj, json=True, from_cache=True):
        if from_cache:
            name = cls._get_cache_name(obj.__class__, obj.id, json)
            cached = cache.get(name)
            if cached:
                logger.debug(f"using cache: {name}")
            else:
                cached = cls._serialize_and_cache(obj, json=json)
            return cached
        else:
            return cls._serialize(obj, json=json)

    @classmethod
    def _serialize(cls, obj, json=False):
        serializer = cls.serializers.get(obj.__class__)
        serialized = serializer(obj).data
        if json:
            serialized = JSONRenderer().render(serialized).decode("utf8")
        return serialized

    @classmethod
    def _serialize_and_cache(cls, obj, json):
        # get expected object names
        name = cls._get_cache_name(obj.__class__, obj.id, json=False)
        json_name = cls._get_cache_name(obj.__class__, obj.id, json=True)

        # serialize data and get json-representation
        if hasattr(obj, "optimized_for_serialization"):
            obj = obj.optimized_for_serialization()
        serialized = cls._serialize(obj, json=False)
        json_str = JSONRenderer().render(serialized).decode("utf8")

        logger.debug(f"setting cache: {name}")
        cache.set_many({name: serialized, json_name: json_str})

        if json:
            return json_str
        else:
            return serialized

    @classmethod
    def add_serializer(cls, model, serializer):
        cls.serializers[model] = serializer

    @classmethod
    def delete_caches(cls, model, ids):
        names = [cls._get_cache_name(model, id, json=False) for id in ids]
        names.extend([cls._get_cache_name(model, id, json=True) for id in ids])
        logger.debug(f"Removing caches: {', '.join(names)}")
        cache.delete_many(names)

    @classmethod
    def clear_cache(cls, Model, filters):
        ids = Model.objects.filter(**filters).values_list("id", flat=True)
        cls.delete_caches(Model, ids)


class ReportExport(NamedTuple):
    """
    Document export.
    """

    docx: Document
    filename: str


class FlatExport(NamedTuple):
    """
    Response class of an exporter method.
    """

    df: pd.DataFrame
    filename: str
    metadata: pd.DataFrame | None = None

    @classmethod
    def api_response(
        cls, df: pd.DataFrame, filename: str, metadata: pd.DataFrame | None = None
    ) -> Response:
        export = cls(df=df, filename=filename, metadata=metadata)
        return Response(export)


class FlatFileExporter:
    """
    Base class used to generate tabular dataset exports.
    """

    def __init__(self, queryset: QuerySet, filename: str = "hawc-export", **kwargs):
        self.queryset = queryset
        self.filename = filename
        self.kwargs = kwargs

    def _get_header_row(self):
        raise NotImplementedError()

    def _get_data_rows(self):
        raise NotImplementedError()

    def build_metadata(self) -> pd.DataFrame | None:
        return None

    @staticmethod
    def get_flattened_tags(dict: dict, key: str) -> str:
        values = [tag.get("name", "") for tag in dict.get(key, [])]
        return f"|{'|'.join(values)}|"

    def build_df(self) -> pd.DataFrame:
        header_row = self._get_header_row()
        data_rows = self._get_data_rows()
        return pd.DataFrame(data=data_rows, columns=header_row)

    def build_export(self) -> FlatExport:
        return FlatExport(
            df=self.build_df(), filename=self.filename, metadata=self.build_metadata()
        )


class WebappConfig(PydanticModel):
    # single-page webapp configuration
    app: str
    page: str | None = None
    data: dict


re_digits = r"\d+"


def get_id_from_choices(items, lookup_value):
    """Checks a Django choice tuple and returns the id that matches the lookup value.

    For example, given items like:

    JERSEY_NUMBERS = (
        (23, "jordan"),
        (99, "gretzky"),
        (56, "taylor")
    )

    Call this function like:

    num = get_id_from_choices(JERSEY_NUMBERS, "TAYLOR")
    # num == 56

    This function will traverse the series of lists/tuples, find the one that matches the
    supplied lookup value, and return another value from that list/tuple.

    This is used for instance by the FlexibleChoiceField, when allowing API clients to supply
    either the internal HAWC code for a given value, or the human-readable name.

    Args:
        items (list, tuple): list of items to search
        lookup_value: the value to search for

    Returns:
        The value, if a single match can be found.

        Returns None if no matches are found.

    Raises:
        ValueError if multiple matches are found.
    """

    # This function used to be a little more generic and could accept these as arguments; no longer
    # needed but keeping them here in case we ever want to expand the function back to what it used to support.
    case_insensitive = True
    lookup_index = 1
    return_index = 0

    if case_insensitive and isinstance(lookup_value, str):
        lookup_value = lookup_value.lower()
        matching_vals = [
            x[return_index] for x in items if str(x[lookup_index]).lower() == lookup_value
        ]
    else:
        matching_vals = [x[return_index] for x in items if x[lookup_index] == lookup_value]

    num_matches = len(matching_vals)
    if num_matches == 0:
        return None
    elif num_matches > 1:
        raise ValueError(f"Found multiple matches when searching {items} for {lookup_value}")
    else:
        return matching_vals[0]


def empty_mpl_figure(title: str = "No data available.") -> Axes:
    """Create a matplotlib figure with no data"""
    plt.figure(figsize=(3, 1))
    plt.axis("off")
    plt.suptitle(title)
    return plt.gca()


def event_plot(series: pd.Series) -> Axes:
    """Return matplotlib event plot"""
    plt.style.use("bmh")

    if series.empty:
        return empty_mpl_figure()

    df = series.to_frame(name="timestamp")
    df.loc[:, "event"] = 1 + (np.random.rand(df.size) - 0.5) / 5  # jitter
    ax = df.plot.scatter(
        x="timestamp",
        y="event",
        c="None",
        edgecolors="blue",
        alpha=1,
        s=80,
        figsize=(15, 5),
        legend=False,
        grid=True,
    )

    # set x axis
    ax.xaxis.set_major_formatter(DateFormatter("%b %d %H:%M"))
    buffer = ((series.max() - series.min()) / 30) + timedelta(seconds=1)
    ax.set_xlim(left=series.min() - buffer, right=pd.Timestamp.utcnow() + buffer)
    ax.set_xlabel("Timestamp (UTC)")

    # set y axis
    ax.set_ybound(0, 2)
    ax.axes.get_yaxis().set_visible(False)

    plt.tight_layout()
    return ax


def reverse_with_query(*args, query: dict, **kwargs):
    """
    Performs Django's `reverse` and appends a query string.

    Args:
        *args: Arguments for Django's `reverse`
        **kwargs: Named arguments for Django's `reverse`
        query (dict): Dictionary to build query string from

    Returns:
        str: reversed url with query string
    """
    url = reverse(*args, **kwargs)
    query = urlencode(query)
    query = f"?{query}" if query else query
    return url + query


reverse_with_query_lazy = lazy(reverse_with_query, str)


class PydanticToDjangoError:
    """
    Context manager to catch pydantic errors and return an appropriate Django/DRF error.

    Has parameters that allow it to be used in several different situations, including:
        For Django: form validation, form field-level validation, model clean methods
        For DRF: viewset validation, serializer validation

    Args:
        include_field (bool): Whether to include a field for the error dict. False can be used for field in form validation, where an error dict is not expected.
        field (str): Field name to associate with error. Defaults to appropriate Django/DRF root field.
        msg (str): Message to use when constructing error. Defaults to a stringified version of the pydantic error.
        drf (bool): Whether to return a DRF error or Django error.

    Raises:
        Django/DRF ValidationError if pydantic ValidationError is raised within the context.
    """

    def __init__(
        self,
        include_field: bool = True,
        field: str | None = None,
        msg: str | None = None,
        drf: bool = False,
    ):
        self.include_field = include_field
        self.field = field if field is not None else "non_field_errors" if drf else "__all__"
        self.msg = msg
        self.drf = drf

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(exc_value, PydanticValidationError):
            if self.msg is None:
                # create error msg from pydantic error
                self.msg = [
                    f"{'->'.join([str(_) for _ in e['loc']])}: {e['msg']}"
                    for e in exc_value.errors()
                ]
            ValidationError = DRFValidationError if self.drf else DjangoValidationError
            raise ValidationError({self.field: self.msg} if self.include_field else self.msg)


T = TypeVar("T")


def cacheable(
    callable: Callable[..., T], cache_key: str, flush: bool = False, cache_duration: int = -1, **kw
) -> T:
    """Get the result from cache or call method to recreate and cache.

    Args:
        callable (Callable): method to evaluation if not found in cache
        cache_key (str): the cache key to get/set
        flush (bool, default False): Force flush the cache and re-evaluate.
        cache_duration (int, default -1): cache key duration; if negative, use settings.CACHE_1_HR.
        **kw: keyword arguments passed to callable

    Returns:
        The result from the callable, either from cache or regenerated.
    """
    if flush:
        cache.delete(cache_key)
    result = cache.get(cache_key)
    if result is None:
        result = callable(**kw)
        if cache_duration < 0:
            cache_duration = settings.CACHE_1_HR
        cache.set(cache_key, result, cache_duration)
    return result


def flatten(lst: Iterable[Iterable]) -> Iterable:
    # given a list of lists (or other iterables), flatten the top-level iterable
    return chain(*(item for item in lst))


def get_current_request() -> HttpRequest:
    """Returns the current request object"""
    return _local_thread.request


def get_current_user():
    """Returns the current request user"""
    return get_current_request().user


def unique_text_list(items: list[str]) -> list[str]:
    """Return a list of unique items in a text list"""
    items = items.copy()
    duplicates = {}
    for i, item in enumerate(items):
        if item in duplicates:
            duplicates[item] += 1
            items[i] = f"{item} ({duplicates[item]})"
        else:
            duplicates[item] = 1
    return items


def get_contrasting_text_color(bg: str) -> str:
    """Returns black or white as text color depending on background color hue.

    Args:
        bg (str): A hex color code, e.g., #123456
    """
    # https://stackoverflow.com/a/41491220/906385
    (r, g, b) = tuple(int(bg[i : i + 2], 16) for i in (1, 3, 5))
    a_type = [r / 255.0, g / 255.0, b / 255.0]
    a_type = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in a_type]
    luminance = 0.2126 * a_type[0] + 0.7152 * a_type[1] + 0.0722 * a_type[2]
    return "#ffffff" if luminance < 0.179 else "#000000"
