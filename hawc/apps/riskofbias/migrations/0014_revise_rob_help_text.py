# Generated by Django 1.10.7 on 2017-08-08 14:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("riskofbias", "0013_auto_20170614_1303"),
    ]

    operations = [
        migrations.AlterField(
            model_name="riskofbiasmetric",
            name="required_animal",
            field=models.BooleanField(
                default=True,
                help_text="Is this metric required for animal bioassay studies?<br/><b>CAUTION:</b> Removing requirement will destroy all bioassay responses previously entered for this metric.",
                verbose_name="Required for bioassay?",
            ),
        ),
        migrations.AlterField(
            model_name="riskofbiasmetric",
            name="required_epi",
            field=models.BooleanField(
                default=True,
                help_text="Is this metric required for human epidemiological studies?<br/><b>CAUTION:</b> Removing requirement will destroy all epi responses previously entered for this metric.",
                verbose_name="Required for epidemiology?",
            ),
        ),
    ]
