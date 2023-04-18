import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


def casrn_to_dtxsid(apps, schema_editor):
    print("casrn_to_dtxsid method removed; see code prior to 2022-01-24")


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0017_dataset"),
    ]

    operations = [
        migrations.CreateModel(
            name="DSSTox",
            fields=[
                (
                    "dtxsid",
                    models.CharField(
                        max_length=80,
                        primary_key=True,
                        serialize=False,
                        verbose_name="DSSTox substance identifier (DTXSID)",
                    ),
                ),
                ("content", django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "DSSTox substance",
                "verbose_name_plural": "DSSTox substances",
                "ordering": ("dtxsid",),
            },
        ),
        migrations.AddField(
            model_name="assessment",
            name="dtxsids",
            field=models.ManyToManyField(
                blank=True,
                related_name="assessments",
                to="assessment.DSSTox",
                verbose_name="DSSTox substance identifiers (DTXSID)",
                help_text="""
        Related <a href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DSSTox</a>
        substance identifiers for this assessment.
        """,
            ),
        ),
        migrations.RunPython(casrn_to_dtxsid, migrations.RunPython.noop),
    ]
