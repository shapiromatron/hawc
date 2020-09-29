from typing import Optional, Set

import django.db.models.deletion
from django.db import migrations, models

from hawc.services.epa.dsstox import DssSubstance


def casrn_to_dtxsid(apps, schema_editor):

    IVChemical = apps.get_model("invitro", "ivchemical")
    DSSTox = apps.get_model("assessment", "dsstox")

    def _create_dsstox(identifier: str) -> Optional[models.Model]:
        try:
            substance = DssSubstance.create_from_identifier(identifier)
            return DSSTox(dtxsid=substance.dtxsid, content=substance.content)
        except ValueError:
            return None

    # list to keep track of dsstox entries for bulk create
    new_dsstox_entries = []

    # existing dtxsids and IVChemical casrns
    existing_dtxsids: Set = set(DSSTox.objects.values_list("dtxsid", flat=True))
    ivchemical_casrns: Set = set(IVChemical.objects.values_list("cas", flat=True))

    # for each casrn...
    for casrn in ivchemical_casrns:
        # create the corresponding DSSTox object
        dsstox = _create_dsstox(casrn)
        # if an error wasn't thrown during creation...
        if dsstox is not None:
            # and the DSSTox object doesn't exist...
            if dsstox.dtxsid not in existing_dtxsids:
                # create the DSSTox object
                new_dsstox_entries.append(dsstox)
                existing_dtxsids.add(dsstox.dtxsid)

    DSSTox.objects.bulk_create(new_dsstox_entries)


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
