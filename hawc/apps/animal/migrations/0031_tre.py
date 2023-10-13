from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0030_django31"),
    ]

    operations = [
        migrations.AddField(
            model_name="endpointgroup",
            name="treatment_effect",
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(0, "not reported"), (1, "yes ↑"), (2, "yes ↓"), (3, "yes"), (4, "no")],
                default=None,
                help_text="Expert judgement based report of treatment related effects (add direction if known). Use when statistical analysis not available. In results comments, indicate whether it was author judgment or assessment team judgement",
                null=True,
            ),
        )
    ]
