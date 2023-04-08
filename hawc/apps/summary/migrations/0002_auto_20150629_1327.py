from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visual",
            name="endpoints",
            field=models.ManyToManyField(
                help_text=b"Endpoints to be included in visualization",
                related_name="visuals",
                to="assessment.BaseEndpoint",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="visual",
            name="studies",
            field=models.ManyToManyField(
                help_text=b"Studies to be included in visualization",
                related_name="visuals",
                to="study.Study",
                blank=True,
            ),
        ),
    ]
