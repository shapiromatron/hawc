# Generated by Django 2.2.15 on 2020-08-20 19:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("assessment", "0018_dsstox"),
        ("epi", "0015_multiple_countries"),
    ]

    operations = [
        migrations.AddField(
            model_name="exposure",
            name="dtxsid",
            field=models.ForeignKey(
                blank=True,
                help_text='<a rel="noopener noreferrer" target="_blank" href="https://www.epa.gov/chemical-research/distributed-structure-searchable-toxicity-dsstox-database">DssTox</a> substance identifier (recommended). When using an identifier, chemical name and CASRN are standardized using the DTXSID.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="exposures",
                to="assessment.DSSTox",
                verbose_name="DSSTox substance identifier (DTXSID)",
            ),
        ),
    ]
