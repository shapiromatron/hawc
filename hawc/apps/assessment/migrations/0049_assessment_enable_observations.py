from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0048_assessment_animal_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="enable_observations",
            field=models.BooleanField(
                default=False,
                help_text="Observations can be used to identify negative effects in animal bioassay studies. The project must use the Toxicity Reference Database Vocabulary to use Observations.",
            ),
        ),
    ]
