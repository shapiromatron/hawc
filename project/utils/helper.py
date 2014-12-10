import decimal
import logging
from collections import OrderedDict
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
        json_str = JSONRenderer().render(serialized)
        serialized = OrderedDict(serialized)  # for pickling

        logging.info('setting cache: {}'.format(name))
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
        logging.info("Removing caches: {}".format(', '.join(names)))
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
        self.wb = xlwt.Workbook()
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
        self.ws = self.wb.add_sheet(sheet_name)

    def _write_header_row(self, header_row):
        # set formatting and freeze panes for header-row
        header_fmt = xlwt.easyxf('font: colour black, bold True;')
        self.ws.set_panes_frozen(True)
        self.ws.horz_split_pos = 1

        # write header-rows
        for col, val in enumerate(header_row):
            self.ws.write(0, col, val, style=header_fmt)

    def _write_data_rows(self, data_rows):

        def try_float(val):
            if type(val) is bool:
                return val
            try:
                return float(val)
            except:
                return val

        r = 0
        for row in data_rows:
            r += 1
            for c, val in enumerate(row):
                self.ws.write(r, c, try_float(val))

    def _django_response(self):
        output = StringIO()
        self.wb.save(output)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="{}.xls"'.format(self.filename)
        return response


class TSVFileBuilder(FlatFile):
    """
    Implementation of FlatFile to generate an tab-separated value file.
    """

    def _setup(self):
        self.output = StringIO()
        self.tsv = unicodecsv.writer(self.output, dialect='excel-tab', encoding='utf-8')

    def _write_header_row(self, header_row):
        self.tsv.writerow(header_row)

    def _write_data_rows(self, data_rows):
        self.tsv.writerows(data_rows)

    def _django_response(self):
        self.output.seek(0)
        response = HttpResponse(self.output, content_type='text/tab-separated-values')
        response['Content-Disposition'] = 'attachment; filename="{}.tsv"'.format(self.filename)
        return response
