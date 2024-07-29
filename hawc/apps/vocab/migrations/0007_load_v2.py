from pathlib import Path

from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    here = Path(__file__).parent
    fixtures = (here / "../fixtures").resolve()
    call_command("loaddata", str(fixtures / "nested_toxref.jsonl"), app_label="vocab")


def unload_fixture(apps, schema_editor):
    apps.get_model("vocab", "Term").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("vocab", "0006_require_uid"),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
