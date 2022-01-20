import json
from typing import Optional, Set

import django.db.models.deletion
from django.db import migrations, models

from hawc.services.epa.dsstox import DssSubstance


def casrn_to_dtxsid(apps, schema_editor):
    Experiment = apps.get_model("animal", "experiment")
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
    updated_experiments = []
    new_dsstox_entries = []
    api_cache = {}

    for experiment in Experiment.objects.exclude(cas=""):

        # try to find a DTXSID instance; hit API cache first; may return None
        if experiment.cas not in api_cache:
            dsstox = _create_dsstox(experiment.cas)
            api_cache[experiment.cas] = dsstox
        else:
            dsstox = api_cache[experiment.cas]

        if dsstox:
            # add new dsstox entry
            if dsstox.dtxsid not in existing_dtxsids:
                new_dsstox_entries.append(dsstox)
                existing_dtxsids.add(dsstox.dtxsid)

            # add experiment entry
            experiment.dtxsid_id = dsstox.dtxsid
            updated_experiments.append(experiment)

            print(
                json.dumps(
                    dict(experiment=experiment.id, casrn=experiment.cas, dtxsid=dsstox.dtxsid)
                )
            )
        else:
            print(json.dumps(dict(experiment=experiment.id, casrn=experiment.cas, dtxsid=None)))

    # bulk create/update items
    DSSTox.objects.bulk_create(new_dsstox_entries)
    Experiment.objects.bulk_update(updated_experiments, ["dtxsid_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0018_dsstox"),
        ("animal", "0025_experiment_has_multiple_generations"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiment",
            name="dtxsid",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="experiments",
                to="assessment.DSSTox",
                verbose_name="DSSTox substance identifier (DTXSID)",
                help_text="""
        <a href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DSSTox</a>
        substance identifier (recommended). When using an identifier, chemical name and CASRN are
        standardized using the DTXSID.
        """,
            ),
        ),
        migrations.RunPython(casrn_to_dtxsid, migrations.RunPython.noop),
    ]
