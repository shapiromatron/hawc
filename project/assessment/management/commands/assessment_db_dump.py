from datetime import datetime
import subprocess
import textwrap

from django.db import connection
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError, OutputWrapper
from django.conf import settings

from assessment.models import Assessment

from django.utils.encoding import force_str


HELP_TEXT = """Dump database for selected assessment."""


class NaiveWrapper(OutputWrapper):
    """
    Simplify writer command to work w/ psql exports
    """

    def write(self, msg, style_func=None, ending=None):
        self._out.write(force_str(msg))


class UnicodeCommand(BaseCommand):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stdout = NaiveWrapper(self.stdout._out)
        self.stderr = NaiveWrapper(self.stderr._out)


class ExternalLibraryExports(object):

    def empty_qs(self, cls):
        # return no rows in table
        return cls.objects.filter(id=-1)

    def complete_qs(self, cls):
        # return all rows in table
        return cls.objects.all()

    def auth_permission(self, cls, ids):
        return self.complete_qs(cls)

    def auth_group(self, cls, ids):
        return self.complete_qs(cls)

    def django_content_type(self, cls, ids):
        return self.complete_qs(cls)

    def django_session(self, cls, ids):
        return cls.objects.filter(session_key='null')

    def django_site(self, cls, ids):
        return self.complete_qs(cls)

    def django_migrations(self, cls, ids):
        return self.complete_qs(cls)

    def django_admin_log(self, cls, ids):
        return self.empty_qs(cls)

    def reversion_revision(self, cls, ids):
        return self.empty_qs(cls)

    def reversion_version(self, cls, ids):
        return self.empty_qs(cls)

    def taggit_tag(self, cls, ids):
        return self.empty_qs(cls)

    def taggit_taggeditem(self, cls, ids):
        return self.empty_qs(cls)

    def lookup(self, dbname):
        return getattr(self, dbname, None)


class BaseHawcDataExports(ExternalLibraryExports):

    def join_querysets_distinct(self, cls, ids):
        querysets = [cls.objects.assessment_qs(_id) for _id in ids]
        query = cls.objects.none()
        for qs in querysets:
            query = (query | qs)
        return query

    def assessment_doseunits(self, cls, ids):
        return self.complete_qs(cls)

    def assessment_species(self, cls, ids):
        return self.complete_qs(cls)

    def assessment_strain(self, cls, ids):
        return self.complete_qs(cls)

    def epi_ethnicity(self, cls, ids):
        return self.complete_qs(cls)

    def myuser_hawcuser(self, cls, ids):
        return self.join_querysets_distinct(cls, ids)

    def myuser_userprofile(self, cls, ids):
        return self.join_querysets_distinct(cls, ids)

class Command(UnicodeCommand):
    help = HELP_TEXT

    header = """\
    --- HAWC ASSESSMENT EXPORT
    --------------------------
    --- Assessment id: {}
    --- Assessment name: {}
    --- Date created: {}


    """

    table_handled = []
    base_tables_handled = []

    def add_arguments(self, parser):
        parser.add_argument('id_list', type=int, nargs='+', help='IDs of the assessments to export, separated by spaces.')

    def write_header(self, assessment):
        header = self.header.format(
            assessment.id,
            assessment,
            datetime.now().isoformat())
        self.stdout.write(textwrap.dedent(header))

    def write_schema_pre_data(self):
        dbname = settings.DATABASES['default']['NAME']
        self.stdout.write('--- HAWC PRE-DATABASE SCHEMA\n')
        self.stdout.write('----------------------------\n')
        proc = subprocess.Popen(
            ['pg_dump', '-d', dbname, '--section=pre-data', '--no-owner'],
            stdout=subprocess.PIPE, shell=False)
        (out, err) = proc.communicate()
        self.stdout.write(out)

    def write_schema_post_data(self):
        dbname = settings.DATABASES['default']['NAME']
        self.stdout.write('--- HAWC POST-DATABASE SCHEMA\n')
        self.stdout.write('-----------------------------\n')
        proc = subprocess.Popen(
            ['pg_dump', '-d', dbname, '--section=post-data', '--no-owner'],
            stdout=subprocess.PIPE, shell=False)
        (out, err) = proc.communicate()
        self.stdout.write(out)

    def write_qs_data(self, qs, model, db_table):
        qry = qs.query.__str__()
        fields = self.get_select_fields(qs.model)
        select_include = self.generate_select(fields, db_table)
        qry_start = 'SELECT DISTINCT' if 'DISTINCT' in qry else 'SELECT'
        qry = "{} {} {}".format(
            qry_start, select_include, qry[qry.find(' FROM'):])
        self.convert_copy(db_table, fields, qry)

        for m2m in model._meta.many_to_many:
            self.write_m2m_data(m2m, qs)

    def write_base_data(self):
        '''
            Exports data that would be duplicated when exporting multiple assessments
        '''
        models = apps.get_models()
        base_exports = BaseHawcDataExports()
        self.stdout.write('--- HAWC BASE DATA\n')
        self.stdout.write('------------------------\n')
        self.cursor = connection.cursor()
        for model in models:
            db_table = model._meta.db_table
            if db_table in self.base_tables_handled:
                continue

            if base_exports.lookup(db_table):
                self.base_tables_handled.append(db_table)
                self.stdout.write("\n--- TABLE {}\n".format(db_table))
                qs = None

                qs = base_exports.lookup(db_table)(model, self.id_list)

                if qs is not None:
                    self.write_qs_data(qs, model, db_table)
                else:
                    self.stdout.write('--- no content added\n')

    def write_data(self, assessment_id):
        self.table_handled = list(self.base_tables_handled)
        self.stdout.write('--- HAWC ASSESSMENT DATA\n')
        self.stdout.write('------------------------\n')
        models = apps.get_models()
        for model in models:
            db_table = model._meta.db_table
            if db_table in self.table_handled:
                continue
            self.table_handled.append(db_table)

            self.stdout.write("\n--- TABLE {}\n".format(db_table))
            qs = None
            if hasattr(model.objects, 'assessment_qs'):
                qs = model.objects.assessment_qs(assessment_id)
            else:
                print(f'--- {model} not exported\n')

            if qs is not None:
                if qs.count() == 0:
                    continue
                self.write_qs_data(qs, model, db_table)

            else:
                self.stdout.write('--- no content added\n')

    def write_m2m_data(self, field, qs):
        db_table = field.m2m_db_table()
        if db_table in self.table_handled:
            return
        self.table_handled.append(db_table)

        ids = tuple(qs.values_list('id', flat=True))
        if len(ids) > 0:
            ids = ', '.join([str(id_) for id_ in ids])
        else:
            ids = '-1'

        matchfield = field.m2m_column_name()
        self.stdout.write("\n--- TABLE {}\n".format(db_table))
        model = getattr(field.model, field.name).through
        fields = self.get_select_fields(model)
        select_include = (self.generate_select(fields, db_table))
        qry = 'SELECT {} FROM "{}" WHERE "{}"."{}" IN ({})'.format(
            select_include,
            db_table,
            db_table,
            matchfield,
            ids,
        )
        self.convert_copy(db_table, fields, qry)

    def convert_copy(self, db_table, fields, qry):
        fields = ['"{}"'.format(fld) for fld in fields]
        selects = ', '.join(fields)
        header = 'COPY {} ({}) FROM stdin;\n'.format(db_table, selects)
        copy = 'COPY ({}) TO STDOUT;'.format(qry)
        self.stdout.write(header)
        self.cursor.copy_expert(copy, self.stdout)
        self.stdout.write('\\.\n')

    def get_select_fields(self, model):
        meta = model._meta
        fields = set(meta.concrete_fields)
        for inherited in meta.get_parent_list():
            fields = fields - set(inherited._meta.concrete_fields)

        db_cols = [fld.get_attname_column()[1] for fld in fields]
        return db_cols

    def generate_select(self, cols, db_table):
        select = ['"{}"."{}"'.format(db_table, col) for col in cols]
        return ", ".join(select)

    def handle(self, *args, **options):

        self.id_list = options.get('id_list', -1)

        self.write_schema_pre_data()
        self.write_base_data()
        for assessment_id in self.id_list:
            assessment = Assessment.objects.filter(id=assessment_id).first()
            if not assessment:
                raise CommandError('Assessment {} not found.'.format(assessment_id))

            self.write_header(assessment)
            self.write_data(assessment.id)

        self.write_schema_post_data()
