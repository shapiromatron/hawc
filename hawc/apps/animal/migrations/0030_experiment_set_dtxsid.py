import json
from typing import Dict

from django.db import migrations


def set_dtxsid(apps, schema_editor):

    Experiment = apps.get_model("animal", "experiment")
    DSSTox = apps.get_model("assessment", "dsstox")

    # list to keep track of changed data for bulk update
    updated_experiments = []

    # casrn to dtxsid in db
    casrn_to_dtxsid: Dict = dict(list(DSSTox.objects.values_list("content__casrn", "dtxsid")))

    # we're only looking at experiments with non-empty chemical identifiers
    for experiment in Experiment.objects.exclude(cas=""):

        dtxsid = casrn_to_dtxsid.get(experiment.cas)

        if dtxsid is not None:
            # add dtxsid to experiment entry
            experiment.dtxsid_id = dtxsid
            updated_experiments.append(experiment)
            print(json.dumps(dict(experiment=experiment.id, casrn=experiment.cas, dtxsid=dtxsid)))
        else:
            print(json.dumps(dict(experiment=experiment.id, casrn=experiment.cas, dtxsid=None)))

    Experiment.objects.bulk_update(updated_experiments, ["dtxsid"])


class Migration(migrations.Migration):

    dependencies = [
        ("animal", "0029_strip_terms"),
    ]

    operations = [
        migrations.RunPython(set_dtxsid, migrations.RunPython.noop),
    ]
