from django.conf import settings
from django.core.management import call_command
from django.db import migrations, models


def load_fixture(apps, schema_editor):
    fixture = settings.PROJECT_PATH / "apps/assessment/fixtures/content.json"
    call_command("loaddata", fixture, app_label="assessment")


def unload_fixture(apps, schema_editor):
    apps.get_model("assessment", "Content").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0025_log_user"),
    ]

    operations = [
        migrations.CreateModel(
            name="Content",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "content_type",
                    models.PositiveIntegerField(
                        choices=[(1, "Homepage"), (2, "About"), (3, "Resources")],
                        unique=True,
                    ),
                ),
                ("template", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("-created",)},
        ),
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
