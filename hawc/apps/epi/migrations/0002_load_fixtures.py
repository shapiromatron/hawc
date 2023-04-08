import os

from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    # Fixtures adapted from:
    # https://www.fsd1.org/powerschool/Documents/PDFs/Federal_Race_Ethnicity_Guidelines.pdf
    # https://www.iso.org/obp/ui/
    fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures"))
    call_command("loaddata", os.path.join(fixture_dir, "ethnicity.json"), app_label="epi")
    call_command("loaddata", os.path.join(fixture_dir, "countries.json"), app_label="epi")
    call_command("loaddata", os.path.join(fixture_dir, "resultmetric.json"), app_label="epi")


def unload_fixture(apps, schema_editor):
    apps.get_model("epi", "Ethnicity").objects.all().delete()
    apps.get_model("epi", "Country").objects.all().delete()
    apps.get_model("epi", "ResultMetric").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("epi", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
