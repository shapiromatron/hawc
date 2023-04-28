from pathlib import Path

from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    here = Path(__file__).parent
    fixtures = (here / "../fixtures").resolve()
    call_command("loaddata", str(fixtures / "states.json"), app_label="eco")
    call_command("loaddata", str(fixtures / "vocab.json"), app_label="eco")
    call_command("loaddata", str(fixtures / "nestedterms.jsonl"), app_label="eco")


def unload_fixture(apps, schema_editor):
    apps.get_model("eco", "Vocab").objects.all().delete()
    apps.get_model("eco", "NestedTerm").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("eco", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
