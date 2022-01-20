import json
from typing import Optional, Set

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models

from hawc.services.epa.dsstox import DssSubstance


def casrn_to_dtxsid(apps, schema_editor):

    Assessment = apps.get_model("assessment", "assessment")
    DSSTox = apps.get_model("assessment", "dsstox")

    def _create_dsstox(identifier: str) -> Optional[models.Model]:
        return None
        try:
            substance = DssSubstance.create_from_identifier(identifier)
            return DSSTox(dtxsid=substance.dtxsid, content=substance.content)
        except ValueError:
            return None

    # lists to keep track of changed data for bulk creates/updates
    existing_dtxsids: Set = set(DSSTox.objects.values_list("dtxsid", flat=True))
    new_assessment_dsstox_m2m_entries = []
    new_dsstox_entries = []

    # we're only looking at assessments with non-empty chemical identifiers
    for assessment in Assessment.objects.exclude(cas=""):

        # try to find a DTXSID instance
        dsstox = _create_dsstox(assessment.cas)

        if dsstox:
            print(
                json.dumps(
                    dict(assessment=assessment.id, casrn=assessment.cas, dtxsid=dsstox.dtxsid)
                )
            )
            # add new dsstox entry
            if dsstox.dtxsid not in existing_dtxsids:
                new_dsstox_entries.append(dsstox)
                existing_dtxsids.add(dsstox.dtxsid)

            # add assessment to dtxsid relation
            m2m = assessment.dtxsids.through(assessment_id=assessment.id, dsstox_id=dsstox.dtxsid)
            new_assessment_dsstox_m2m_entries.append(m2m)
        else:
            print(json.dumps(dict(assessment=assessment.id, casrn=assessment.cas, dtxsid=None)))

    # bulk create items
    DSSTox.objects.bulk_create(new_dsstox_entries)
    Assessment.dtxsids.through.objects.bulk_create(new_assessment_dsstox_m2m_entries)


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
