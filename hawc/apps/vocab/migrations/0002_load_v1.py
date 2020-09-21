"""
Bulk-load initial data from a CSV.

While it took longer to write, it should load much more quickly.
If these become problematic, default to `manage.py dumpdata/loaddata`
"""
from io import StringIO
from typing import List

from django.conf import settings
from django.db import connection, migrations

CSV_NAME = settings.PROJECT_PATH / "apps/vocab/fixtures/v1.csv"


def _get_headers(cursor) -> List[str]:
    cursor.execute("Select * FROM vocab_term LIMIT 0")
    return [desc[0] for desc in cursor.description]


def _generate_data_fixture():
    # unused; describe how data was generated
    with connection.client.connection.cursor() as cursor:
        f = StringIO()
        headers = _get_headers(cursor)
        cursor.copy_to(f, "vocab_term", columns=headers)
        assert len(f.getvalue()) > 0

    f.seek(0)
    CSV_NAME.write_text(f.getvalue())


def bulk_load(apps, schema_editor):
    """Load v1 of vocabulary"""
    with connection.client.connection.cursor() as cursor:
        # get headers
        headers = _get_headers(cursor)

        # ensure we're starting with a fresh table
        cursor.execute("SELECT COUNT(id) FROM vocab_term")
        if cursor.fetchone()[0] != 0:
            raise ValueError("Content not deleted.")

        # reset id sequence
        cursor.execute("ALTER SEQUENCE vocab_term_id_seq RESTART WITH 1")

        # load data
        f = CSV_NAME.open()
        cursor.copy_from(f, "vocab_term", columns=headers)
        cursor.execute("SELECT COUNT(id) FROM vocab_term")
        if cursor.fetchone()[0] == 0:
            raise ValueError("No content loaded.")

        # reset id sequence
        cursor.execute("SELECT MAX(id) FROM vocab_term")
        max_id = cursor.fetchone()[0]
        cursor.execute(f"ALTER SEQUENCE vocab_term_id_seq RESTART WITH {max_id+1}")


def bulk_delete(apps, schema_editor):
    with connection.client.connection.cursor() as cursor:
        # truncate table
        cursor.execute("TRUNCATE TABLE vocab_term CASCADE")
        cursor.execute("SELECT COUNT(id) FROM vocab_term")
        assert cursor.fetchone()[0] == 0

        # reset id sequence
        cursor.execute("ALTER SEQUENCE vocab_term_id_seq RESTART WITH 1")


class Migration(migrations.Migration):

    dependencies = [
        ("vocab", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(bulk_load, bulk_delete),
    ]
