from django.conf import settings
from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    fixture = settings.PROJECT_PATH / "apps/assessment/fixtures/content_v2.json"
    call_command("loaddata", fixture, app_label="assessment")


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0026_content"),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
