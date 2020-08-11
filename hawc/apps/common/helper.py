import decimal
import hashlib
import logging
import re
import uuid
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Optional

import pandas as pd
from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import QuerySet
from django.utils import html
from django.utils.encoding import force_text
from rest_framework.renderers import JSONRenderer


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
    return re.sub(r"&(?:\w+|#\d+);", "", force_text(value))


def strip_tags(value):
    """Return the given HTML with all tags stripped."""
    # Note: in typical case this loop executes _strip_once once. Loop condition
    # is redundant, but helps to reduce number of executions of _strip_once.
    # Note: Originally in Django but removed in v1.10
    while "<" in value and ">" in value:
        new_value = html._strip_once(value)
        if new_value == value:
            # _strip_once was not able to detect more tags
            break
        value = new_value
    return value


def listToUl(list_):
    return f"<ul>{''.join(['<li>{0}</li>'.format(d) for d in list_])}</ul>"


def tryParseInt(val, default=None):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def try_parse_list_ints(val: str = None) -> List[int]:
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


def create_uuid(id: int) -> str:
    """
    Creates a UUID from a given ID
    """
    hashed_id = hashlib.md5(str(id).encode())
    hashed_id.update(settings.SECRET_KEY.encode())
    return str(uuid.UUID(bytes=hashed_id.digest()))


def df_move_column(df: pd.DataFrame, target: str, after: Optional[str] = None) -> pd.DataFrame:
    """Move target column after another column.

    Args:
        df (pd.DataFrame): The dataframe to modify.
        target (str): Name of the column to move
        after (Optional[str], optional): Name of column to move after; if None, puts first.

    Returns:
        pd.DataFrame: The mutated dataframe.
    """
    cols = df.columns.tolist()
    target_name = cols.pop(cols.index(target))
    insert_index = cols.index(after) + 1 if after else 0
    cols.insert(insert_index, target_name)
    return df[cols]


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
                logging.debug(f"using cache: {name}")
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
        serialized = OrderedDict(serialized)  # for pickling

        logging.debug(f"setting cache: {name}")
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
        logging.debug(f"Removing caches: {', '.join(names)}")
        cache.delete_many(names)

    @classmethod
    def clear_cache(cls, Model, filters):
        ids = Model.objects.filter(**filters).values_list("id", flat=True)
        cls.delete_caches(Model, ids)


@dataclass(frozen=True)
class FlatExport:
    """
    Response class of an exporter method.
    """

    df: pd.DataFrame
    filename: str


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

    @staticmethod
    def get_flattened_tags(dict: Dict, key: str) -> str:
        values = [tag.get("name", "") for tag in dict.get(key, [])]
        return f"|{'|'.join(values)}|"

    def build_df(self) -> pd.DataFrame:
        header_row = self._get_header_row()
        data_rows = self._get_data_rows()
        return pd.DataFrame(data=data_rows, columns=header_row)

    def build_export(self) -> FlatExport:
        df = self.build_df()
        return FlatExport(df, self.filename)


re_digits = r"\d+"
