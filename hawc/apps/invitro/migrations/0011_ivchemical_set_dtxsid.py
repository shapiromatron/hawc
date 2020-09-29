import json
from typing import Dict

from django.db import migrations


def set_dtxsid(apps, schema_editor):

    IVChemical = apps.get_model("invitro", "ivchemical")
    DSSTox = apps.get_model("assessment", "dsstox")

    # list to keep track of changed data for bulk update
    updated_ivchemicals = []

    # casrn to dtxsid in db
    casrn_to_dtxsid: Dict = dict(list(DSSTox.objects.values_list("content__casrn", "dtxsid")))

    # we're only looking at ivchemicals with non-empty chemical identifiers
    for ivchemical in IVChemical.objects.exclude(cas=""):

        dtxsid = casrn_to_dtxsid.get(ivchemical.cas)

        if dtxsid is not None:
            # add dtxsid to ivchemical entry
            ivchemical.dtxsid_id = dtxsid
            updated_ivchemicals.append(ivchemical)
            print(json.dumps(dict(ivchemical=ivchemical.id, casrn=ivchemical.cas, dtxsid=dtxsid)))
        else:
            print(json.dumps(dict(ivchemical=ivchemical.id, casrn=ivchemical.cas, dtxsid=None)))

    IVChemical.objects.bulk_update(updated_ivchemicals, ["dtxsid"])


class Migration(migrations.Migration):

    dependencies = [
        ("invitro", "0010_endpoint_ordering"),
    ]

    operations = [
        migrations.RunPython(set_dtxsid, migrations.RunPython.noop),
    ]
