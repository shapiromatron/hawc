import textwrap
from datetime import datetime
import subprocess

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
        super(UnicodeCommand, self).__init__(**kwargs)
        self.stdout = NaiveWrapper(self.stdout._out)
        self.stderr = NaiveWrapper(self.stderr._out)


class ExternalLibraryExports(object):

    def empty_qs(self, cls):
        # return a deliberately emtpy table of results
        return cls.objects.filter(id=-1)

    def complete_qs(self, cls):
        return cls.objects.all()

    def auth_permission(self, cls, assessment_id):
        return self.empty_qs(cls)

    def auth_group(self, cls, assessment_id):
        return self.empty_qs(cls)

    def django_content_type(self, cls, assessment_id):
        return self.complete_qs(cls)

    def django_session(self, cls, assessment_id):
        return cls.objects.filter(session_key='null')

    def django_site(self, cls, assessment_id):
        return self.empty_qs(cls)

    def django_admin_log(self, cls, assessment_id):
        return self.empty_qs(cls)

    def reversion_revision(self, cls, assessment_id):
        return self.empty_qs(cls)

    def reversion_version(self, cls, assessment_id):
        return self.empty_qs(cls)

    def taggit_tag(self, cls, assessment_id):
        return self.empty_qs(cls)

    def taggit_taggeditem(self, cls, assessment_id):
        return self.empty_qs(cls)

    def lookup(self, dbname):
        return getattr(self, dbname, None)


class Command(UnicodeCommand):
    help = HELP_TEXT

    header = """\
    --- HAWC ASSESSMENT EXPORT
    --------------------------
    --- Assessment id: {}
    --- Assessment name: {}
    --- Date created: {}


    """

    handled_m2m = []

    def add_arguments(self, parser):
        parser.add_argument('assessment_id', type=int)

    def write_header(self, assessment):
        header = self.header.format(
            assessment.id,
            assessment,
            datetime.now().isoformat())
        self.stdout.write(textwrap.dedent(header))

    def write_schema(self):
        dbname = settings.DATABASES['default']['NAME']
        self.stdout.write('--- HAWC DATABASE SCHEMA\n')
        self.stdout.write('------------------------\n')
        proc = subprocess.Popen(
            ['pg_dump', '-s', dbname],
            stdout=subprocess.PIPE, shell=False)
        (out, err) = proc.communicate()
        self.stdout.write(out)

    def write_data(self, assessment_id):
        external_exports = ExternalLibraryExports()
        self.stdout.write('--- HAWC ASSESSMENT DATA\n')
        self.stdout.write('------------------------\n')
        self.cursor = connection.cursor()
        models = apps.get_models()
        for model in models:
            db_table = model._meta.db_table
            self.stdout.write("\n# TABLE {}\n".format(db_table))
            qs = None
            if hasattr(model, 'assessment_qs'):
                qs = model.assessment_qs(assessment_id)
            elif external_exports.lookup(db_table):
                qs = external_exports.lookup(db_table)(model, assessment_id)

            if qs is not None:
                querystr = qs.query.__str__()
                qry = "COPY ({}) TO STDOUT WITH CSV HEADER;".format(querystr)
                self.cursor.copy_expert(qry, self.stdout)
                for m2m in model._meta.many_to_many:
                    self.write_m2m_data(m2m, qs)

            else:
                self.stdout.write('# no content added\n')

    def write_m2m_data(self, field, qs):
        db_table = field.m2m_db_table()
        if db_table in self.handled_m2m:
            return
        self.handled_m2m.append(db_table)

        ids = tuple(qs.values_list('id', flat=True))
        if len(ids) > 0:
            ids = ', '.join([str(id_) for id_ in ids])
        else:
            ids = '-1'

        field = field.m2m_column_name()
        self.stdout.write("\n# TABLE {}\n".format(db_table))
        qry = 'COPY (SELECT * FROM "{}" WHERE "{}"."{}" IN ({})) TO STDOUT WITH CSV HEADER;'.format(  # noqa
            db_table,
            db_table,
            field,
            ids,
        )
        self.cursor.copy_expert(qry, self.stdout)

    def handle(self, *args, **options):
        assessment_id = options.get('assessment_id', -1)
        assessment = Assessment.objects.filter(id=assessment_id).first()
        if not assessment:
            raise CommandError('Assessment {} not found.'.format(assessment_id))

        self.write_header(assessment)
        self.write_schema()
        self.write_data(assessment.id)
