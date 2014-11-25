import decimal
import logging
from StringIO import StringIO
import os
import re

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import HttpResponse

from rest_framework.renderers import JSONRenderer

import unicodecsv
from docx import Document
import xlwt


class HAWCDjangoJSONEncoder(DjangoJSONEncoder):
    """
    Modified to return a float instead of a string.
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        else:
            return super(HAWCDjangoJSONEncoder, self).default(o)


class HAWCdocx(object):

    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), 'hawc-template.docx')
        self.doc = Document(path)

    @classmethod
    def to_date_string(cls, datetime):
        """
        Helper function to ensure dates are constant throughout report.
        """
        return datetime.strftime("%B %d %Y, %I:%M %p")

    def django_response(self):
        """
        Create an HttpResponse object with the appropriate headers.
        """
        docx_file = StringIO()
        self.doc.save(docx_file)
        docx_file.seek(0)
        response = HttpResponse(docx_file)
        response['Content-Disposition'] = 'attachment; filename=example.docx'
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return response


def build_tsv_file(headers, queryset, *args, **kwargs):
    """
    Construct a tab-delimited version of the selected queryset of objects.

    - headers: list of header names
    - queryset: list of objects, each of which has a flat_file_row method

    Returns a tab-delimited StringIO object.

    """
    output = StringIO()
    writer = unicodecsv.writer(output, dialect='excel-tab', encoding='utf-8')
    writer.writerow(headers)
    for obj in queryset:
        writer.writerows(obj.flat_file_row(*args, **kwargs))
    output.seek(0)
    return output



def excel_export_detail(dic, isHeader, blacklist=()):
    """
    General function used build an appropriate list of items for an excel
    export given an Ordered Dictionary; returns either the keys or values.
    """
    keys = []
    vals = []
    for key, val in dic.viewitems():
        if key[0] != "_" and key not in blacklist:
            keys.append(key)
            vals.append(val)
    if isHeader:
        return keys
    else:
        return vals


def build_excel_file(sheet_name, headers, queryset, data_rows_func, *args, **kwargs):
    """
    Construct an Excel workbook of the selected queryset of endpoints.

    - sheet_name: worksheet name for workbook
    - headers: list of header names
    - queryset: list of objects, each of which has a flat_file_row method
    - data_rows_func: custom function which constructs excel rows

    Returns an Excel StringIO object.

    """
    def clean_ws_name(name="Sheet1"):
        """
        http://stackoverflow.com/questions/451452/
        While renaming a sheet or chart, you entered an invalid name. Try one of the following:
        - Make sure the name you entered does not exceed 31 characters.
        - Make sure the name does not contain any of the following characters: : \ / ? * [ or ]
        - Make sure you did not leave the name blank.
        """
        return re.sub(r'[\:\\/\?\*\[\]]+', r'-', name)[:31]

    wb = xlwt.Workbook()
    ws = wb.add_sheet(clean_ws_name(sheet_name))

    header_fmt = xlwt.easyxf('font: colour black, bold True;')

    # freeze panes on header
    ws.set_panes_frozen(True)
    ws.horz_split_pos = 1

    # write header
    for col, val in enumerate(headers):
        ws.write(0, col, val, style=header_fmt)

    data_rows_func(ws, queryset, *args, **kwargs)

    # save as object
    output = StringIO()
    wb.save(output)
    output.seek(0)

    return output


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
        if json: name += ".json"
        return name

    @classmethod
    def get_serialized(cls, obj, json=True, from_cache=True):
        if from_cache:
            name = cls._get_cache_name(obj.__class__, obj.id, json)
            cached = cache.get(name)
            if cached:
                logging.info('using cache: {}'.format(name))
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
        serialized = cls._serialize(obj, json=False)
        json = JSONRenderer().render(serialized)

        logging.info('setting cache: {}'.format(name))
        cache.set_many({name: serialized, json_name: json})

        if json:
            return json
        else:
            return serialized

    @classmethod
    def add_serializer(cls, model, serializer):
        cls.serializers[model] = serializer

    @classmethod
    def delete_caches(cls, model, ids):
        names = [cls._get_cache_name(model, id, json=False) for id in ids]
        names.extend([cls._get_cache_name(model, id, json=True) for id in ids])
        logging.info("Removing caches: {}".format(', '.join(names)))
        cache.delete_many(names)
