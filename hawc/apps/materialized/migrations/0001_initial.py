from django.db import migrations, models

from ..sql import FinalRiskOfBiasScore


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("riskofbias", "0022_new_rob_scores"),
    ]

    operations = [
        migrations.RunSQL(FinalRiskOfBiasScore.create, FinalRiskOfBiasScore.drop),
        migrations.CreateModel(
            name="FinalRiskOfBiasScore",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("score_score", models.SmallIntegerField(verbose_name="Score")),
                ("is_default", models.BooleanField()),
                ("object_id", models.IntegerField(null=True)),
            ],
            options={"abstract": False, "managed": False},
        ),
    ]
