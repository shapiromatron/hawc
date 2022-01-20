import json
from typing import Optional, Set

import django.db.models.deletion
from django.db import migrations, models

from hawc.services.epa.dsstox import DssSubstance


def casrn_to_dtxsid(apps, schema_editor):

    IVChemical = apps.get_model("invitro", "ivchemical")
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
    updated_ivchemicals = []
    new_dsstox_entries = []
    api_cache = {}

    # we're only looking at ivchemicals with non-empty chemical identifiers
    for ivchemical in IVChemical.objects.exclude(cas=""):

        # try to find a DTXSID instance; hit API cache first; may return None
        if ivchemical.cas not in api_cache:
            dsstox = _create_dsstox(ivchemical.cas)
            api_cache[ivchemical.cas] = dsstox
        else:
            dsstox = api_cache[ivchemical.cas]

        if dsstox:
            # add new dsstox entry
            if dsstox.dtxsid not in existing_dtxsids:
                new_dsstox_entries.append(dsstox)
                existing_dtxsids.add(dsstox.dtxsid)

            # add ivchemical entry
            ivchemical.dtxsid_id = dsstox.dtxsid
            updated_ivchemicals.append(ivchemical)

            print(
                json.dumps(
                    dict(ivchemical=ivchemical.id, casrn=ivchemical.cas, dtxsid=dsstox.dtxsid)
                )
            )
        else:
            print(json.dumps(dict(ivchemical=ivchemical.id, casrn=ivchemical.cas, dtxsid=None)))

    DSSTox.objects.bulk_create(new_dsstox_entries)
    IVChemical.objects.bulk_update(updated_ivchemicals, ["dtxsid_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0018_dsstox"),
        ("invitro", "0008_auto_20190416_2003"),
    ]

    operations = [
        migrations.AddField(
            model_name="ivchemical",
            name="dtxsid",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="ivchemicals",
                to="assessment.DSSTox",
                verbose_name="DSSTox substance identifier (DTXSID)",
                help_text="""
        <a href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DSSTox</a>
        substance identifier (recommended). When using an identifier, name is standardized using the DTXSID.
        """,
            ),
        ),
        migrations.RunPython(casrn_to_dtxsid, migrations.RunPython.noop),
    ]
