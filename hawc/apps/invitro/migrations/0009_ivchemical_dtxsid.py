import django.db.models.deletion
from django.db import migrations, models


def casrn_to_dtxsid(apps, schema_editor):
    print("casrn_to_dtxsid method removed; see code prior to 2022-01-24")


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
                help_text='<a rel="noopener noreferrer" target="_blank" href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DssTox</a> substance identifier (recommended). When using an identifier, chemical name and CASRN are standardized using the <a href="https://comptox.epa.gov/dashboard/" rel="noopener noreferrer" target="_blank">DTXSID</a>.',
            ),
        ),
        migrations.RunPython(casrn_to_dtxsid, migrations.RunPython.noop),
    ]
