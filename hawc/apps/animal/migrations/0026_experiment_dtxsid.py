# Generated by Django 2.2.11 on 2020-08-06 13:29

import django.db.models.deletion
import requests
from django.db import migrations, models


def casrn_to_dtxsid(apps, schema_editor):

    Experiment = apps.get_model("animal", "experiment")
    DSSTox = apps.get_model("assessment", "dsstox")

    def _create_dsstox(identifier):
        # return an instance of dsstox or None if its not found
        url = f"https://actorws.epa.gov/actorws/chemIdentifier/v01/resolve.json?identifier={identifier}"
        response = requests.get(url)
        response_dict = response.json()["DataRow"]
        if not response_dict["dtxsid"]:
            return None
        else:
            return DSSTox(dtxsid=response_dict["dtxsid"], content=response.text)

    # we're only looking at experiments with non-empty chemical identifiers
    experiments = Experiment.objects.exclude(cas="")

    # lists to keep track of changed data for bulk creates/updates
    existing_dtxsids = list(DSSTox.objects.all().values_list("dtxsid", flat=True))
    updated_experiments = list()
    dsstox_entries = list()

    for experiment in experiments:
        dsstox = _create_dsstox(experiment.cas)
        # if there is an associated DTXSID...
        if dsstox:
            # add it to experiment
            experiment.dtxsid = dsstox
            # mark the experiment as changed
            updated_experiments.append(experiment)
            # and create the dsstox entry if it doesn't exist
            if dsstox.dtxsid not in existing_dtxsids:
                dsstox_entries.append(dsstox)
                existing_dtxsids.append(dsstox.dtxsid)

    # create new dsstox entries
    DSSTox.objects.bulk_create(dsstox_entries)
    # update experiments with dtxsid
    Experiment.objects.bulk_update(updated_experiments, ["dtxsid"])


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0018_auto_20200806_0929"),
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
            ),
        ),
        migrations.RunPython(casrn_to_dtxsid, migrations.RunPython.noop),
    ]
