import decimal
import hashlib
import logging
import re
import uuid
from collections import OrderedDict
from io import BytesIO

import pandas as pd
from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils import html
from django.utils.encoding import force_text
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


def HAWCtoDateString(datetime):
    """
    Helper function to ensure dates are consistent.
    """
    return datetime.strftime("%B %d %Y, %I:%M %p")


def cleanHTML(txt):
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


def create_uuid(id: int) -> str:
    """
    Creates a UUID from a given ID
    """
    hashed_id = hashlib.md5(str(id).encode())
    hashed_id.update(settings.SECRET_KEY.encode())
    return str(uuid.UUID(bytes=hashed_id.digest()))


class HAWCDjangoJSONEncoder(DjangoJSONEncoder):
    """
    Modified to return a float instead of a string.
    """

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        else:
            return super().default(o)


class SerializerHelper(object):
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


class FlatFileExporter(object):
    """
    Base class used to generate flat-file exports of serialized data.
    """

    def __init__(self, queryset, export_format, filename="download", **kwargs):
        self.queryset = queryset
        self.export_format = export_format
        self.filename = filename
        self.kwargs = kwargs

    def _get_header_row(self):
        raise NotImplementedError()

    def _get_data_rows(self):
        raise NotImplementedError()

    @classmethod
    def _get_tags(cls, e):
        returnValue = ""

        if "effects" in e:
            """ This element is an Outcome element with an "effects" field """
            effects = [tag["name"] for tag in e["effects"]]

            if len(effects) > 0:
                returnValue = f"|{'|'.join(effects)}|"
        elif "resulttags" in e:
            """ This element is a Result element with a "resulttags" field """
            resulttags = [tag["name"] for tag in e["resulttags"]]

            if len(resulttags) > 0:
                returnValue = f"|{'|'.join(resulttags)}|"

        return returnValue

    def build_response(self):
        header_row = self._get_header_row()
        data_rows = self._get_data_rows()
        df = pd.DataFrame(data=data_rows, columns=header_row)

        if self.export_format == "api":
            return Response(df)

        elif self.export_format == "tsv":
            response = HttpResponse(
                df.to_csv(sep="\t", index=False), content_type="text/tab-separated-values"
            )
            response["Content-Disposition"] = f'attachment; filename="{self.filename}.tsv"'
            return response

        elif self.export_format == "excel":
            # We have to remove the timezone from datetime objects to make it Excel compatible
            ## Note: DataFrame update doesn't preserve dtype, so we must iterate through the columns instead
            df_datetime = df.select_dtypes(include="datetimetz").apply(
                lambda x: x.dt.tz_localize(None)
            )
            for col in df_datetime.columns:
                df[col] = df_datetime[col]

            f = BytesIO()
            with pd.ExcelWriter(
                f, date_format="YYYY-MM-DD", datetime_format="YYYY-MM-DD HH:MM:SS"
            ) as writer:
                df.to_excel(writer, index=False)

            response = HttpResponse(
                f.getvalue(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f'attachment; filename="{self.filename}.xlsx"'
            return response

        else:
            raise ValueError(f"export_format not found: {self.export_format}")
