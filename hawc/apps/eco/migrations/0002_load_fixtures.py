# -*- coding: utf-8 -*-


import os

from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):

    fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures"))
    call_command(
        "loaddata", os.path.join(fixture_dir, "countries.json"), app_label="eco"
    )  # copied from epi countries fixture
    call_command("loaddata", os.path.join(fixture_dir, "climates.json"), app_label="eco")
    call_command("loaddata", os.path.join(fixture_dir, "ecoregions.json"), app_label="eco")
    call_command("loaddata", os.path.join(fixture_dir, "states.json"), app_label="eco")


def unload_fixture(apps, schema_editor):
    apps.get_model("eco", "Country").objects.all().delete()
    apps.get_model("eco", "Climate").objects.all().delete()
    apps.get_model("eco", "Ecoregion").objects.all().delete()
    apps.get_model("eco", "State").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("eco", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
