from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("epi", "0003_auto_20151014_1445"),
    ]

    operations = [
        migrations.AddField(
            model_name="exposure",
            name="age_of_exposure",
            field=models.CharField(
                help_text=b'Textual age description for when exposure measurement sample was taken, treatment given, or age for which survey data apply [examples include:  specific age indicated in the study (e.g., "gestational week 20, 3 years of age, 10-12 years of age, previous 12 months") OR standard age categories: "fetal (in utero), neonatal (0-27 days), infancy (1-12 months) toddler (1-2 years), middle childhood (6-11 years, early adolescence (12-18 years),late adolescence (19-21 years), adulthood (>21),older adulthood (varies)" \xe2\x80\x93 based on NICHD Integratedpediatric terminology]',
                max_length=32,
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="outcome",
            name="age_of_measurement",
            field=models.CharField(
                help_text=b'Textual age description when outcomes were measured [examples include:  specific age indicated in the study (e.g., "3 years of age, 10-12 years of age") OR standard age categories: "infancy (1-12 months), toddler (1-2 years), middle childhood (6-11 years, early adolescence (12-18 years), late adolescence (19-21 years), adulthood (>21), older adulthood (varies)" - based on NICHD Integrated pediatric terminology]',
                max_length=32,
                verbose_name=b"Age at outcome measurement",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="outcome",
            name="effect_subtype",
            field=models.CharField(
                help_text=b"Effect subtype, using common-vocabulary",
                max_length=128,
                blank=True,
            ),
        ),
    ]
