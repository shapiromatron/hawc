from datetime import datetime
import decimal
import logging
from collections import OrderedDict
from io import BytesIO, StringIO
import re

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import HttpResponse
from django.utils import html

from rest_framework.renderers import JSONRenderer

import csv
import xlsxwriter


def HAWCtoDateString(datetime):
    """
    Helper function to ensure dates are consistent.
    """
    return datetime.strftime("%B %d %Y, %I:%M %p")


def cleanHTML(txt):
    return strip_entities(
        strip_tags(
            txt.replace('\n', ' ')
               .replace('\r', "")
               .replace('<br>', "\n")
               .replace("&nbsp;", " ")))


def strip_entities(value):
    """Return the given HTML with all entities (&something;) stripped."""
    # Note: Originally in Django but removed in v1.10
    return re.sub(r'&(?:\w+|#\d+);', '', html.force_text(value))


def strip_tags(value):
    """Return the given HTML with all tags stripped."""
    # Note: in typical case this loop executes _strip_once once. Loop condition
    # is redundant, but helps to reduce number of executions of _strip_once.
    # Note: Originally in Django but removed in v1.10
    while '<' in value and '>' in value:
        new_value = html._strip_once(value)
        if new_value == value:
            # _strip_once was not able to detect more tags
            break
        value = new_value
    return value


def listToUl(list_):
    return "<ul>{0}</ul>".format(
        "".join(["<li>{0}</li>".format(d) for d in list_]))


def tryParseInt(val, default=None):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


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
        name = "{}.{}.{}".format(model.__module__, model.__name__, id)
        if json:
            name += ".json"
        return name

    @classmethod
    def get_serialized(cls, obj, json=True, from_cache=True):
        if from_cache:
            name = cls._get_cache_name(obj.__class__, obj.id, json)
            cached = cache.get(name)
            if cached:
                logging.debug('using cache: {}'.format(name))
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
            serialized = JSONRenderer().render(serialized)
        return serialized

    @classmethod
    def _serialize_and_cache(cls, obj, json):
        # get expected object names
        name = cls._get_cache_name(obj.__class__, obj.id, json=False)
        json_name = cls._get_cache_name(obj.__class__, obj.id, json=True)

        # serialize data and get json-representation
        if hasattr(obj, 'optimized_for_serialization'):
            obj = obj.optimized_for_serialization()
        serialized = cls._serialize(obj, json=False)
        json_str = JSONRenderer().render(serialized)
        serialized = OrderedDict(serialized)  # for pickling

        logging.debug('setting cache: {}'.format(name))
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
        logging.debug("Removing caches: {}".format(', '.join(names)))
        cache.delete_many(names)


class FlatFileExporter(object):
    """
    Base class used to generate flat-file exports of serialized data.
    """
    def __init__(self, queryset, export_format, **kwargs):
        self.queryset = queryset
        self.export_format = export_format
        self.kwargs = kwargs

        if self.export_format == "tsv":
            self.exporter = TSVFileBuilder(**kwargs)
        elif self.export_format == "excel":
            self.exporter = ExcelFileBuilder(**kwargs)
        else:
            raise ValueError("export_format not found: {}".format(self.export_format))

    def _get_header_row(self):
        raise NotImplementedError()

    def _get_data_rows(self):
        raise NotImplementedError()

    @classmethod
    def _get_tags(cls, e):
        returnValue = ""

        if ("effects" in e):
            effects = [tag["name"] for tag in e["effects"]]

            if (len(effects) > 0):
                returnValue = "|{0}|".format("|".join(effects))

        return returnValue

    def build_response(self):
        header_row = self._get_header_row()
        data_rows = self._get_data_rows()
        return self.exporter.generate_response(header_row, data_rows)


class FlatFile(object):
    """
    Generic file-builder object, providing an interface for generation of
    some-type of flat-file-export.

    Optional initialization argument:

        - `filename`: String filename, without extension (default: "download")
    """

    def __init__(self, filename="download", **kwargs):
        self.filename = filename
        self.kwargs = kwargs

    def generate_response(self, header_row, data_rows):
        self._setup()
        self._write_header_row(header_row)
        self._write_data_rows(data_rows)
        return self._django_response()

    def _setup(self):
        raise NotImplementedError()

    def _write_header_row(self, header_row):
        # `header_row` is a list of strings
        raise NotImplementedError()

    def _write_data_rows(self, data_rows):
        # `data_rows` is a list of lists
        raise NotImplementedError()

    def _django_response(self):
        raise NotImplementedError()


class ExcelFileBuilder(FlatFile):
    """
    Implementation of FlatFile to generate an Excel workbook with a single
    Excel worksheet. Has one header row with minor styles applied.

    Optional initialization argument:

    - `sheet_name`: String name of worksheet (default: "Sheet1")

    """

    def _setup(self):
        self.output = BytesIO()
        self.wb = xlsxwriter.Workbook(self.output)
        self._add_worksheet(sheet_name=self.kwargs.get("sheet_name", "Sheet1"))

    def _add_worksheet(self, sheet_name="Sheet1"):
        """
        Create a new blank worksheet, and make sure the worksheet name is valid:
        - Make sure the name you entered does not exceed 31 characters.
        - Make sure the name does not contain any of the following characters: : \ / ? * [ or ]
        - Make sure you did not leave the name blank.
        http://stackoverflow.com/questions/451452/
        """
        sheet_name = re.sub(r'[\:\\/\?\*\[\]]+', r'-', sheet_name)[:31]
        self.ws = self.wb.add_worksheet(sheet_name)

    def _write_header_row(self, header_row):
        # set formatting and freeze panes for header-row
        header_fmt = self.wb.add_format({'bold': True})
        self.ws.freeze_panes(1, 0)
        self.ncols = len(header_row)

        # write header-rows
        for col, val in enumerate(header_row):
            self.ws.write(0, col, val, header_fmt)

    def _write_data_rows(self, data_rows):
        date_format = self.wb.add_format({'num_format': 'dd/mm/yy'})

        def write_cell(r, c, val):
            if type(val) is bool:
                return self.ws.write_boolean(r, c, val)
            elif type(val) is datetime:
                return self.ws.write_datetime(r, c, val.replace(tzinfo=None), date_format)

            try:
                val = float(val)
            except:
                pass

            return self.ws.write(r, c, val)

        r = 0
        for row in data_rows:
            r += 1
            for c, val in enumerate(row):
                write_cell(r, c, val)

        self.ws.autofilter(0, 0, r, self.ncols - 1)

    def _django_response(self):
        fn = '{}.xlsx'.format(self.filename)
        self.wb.close()
        self.output.seek(0)
        response = HttpResponse(self.output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(fn)
        return response


class TSVFileBuilder(FlatFile):
    """
    Implementation of FlatFile to generate an tab-separated value file.
    """

    def _setup(self):
        self.output = StringIO()
        self.tsv = csv.writer(self.output, dialect='excel-tab')

    def _write_header_row(self, header_row):
        self.tsv.writerow(header_row)

    def _write_data_rows(self, data_rows):
        self.tsv.writerows(data_rows)

    def _django_response(self):
        self.output.seek(0)
        response = HttpResponse(self.output, content_type='text/tab-separated-values')
        response['Content-Disposition'] = 'attachment; filename="{}.tsv"'.format(self.filename)
        return response
