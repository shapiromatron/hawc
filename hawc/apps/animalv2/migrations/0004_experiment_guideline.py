from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animalv2", "0003_add_ordering"),
    ]

    operations = [
        migrations.AddField(
            model_name="experiment",
            name="guideline",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.CreateModel(
            name="Observation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("tested_status", models.BooleanField(default=False)),
                ("reported_status", models.BooleanField(default=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "endpoint",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.CASCADE,
                        to="vocab.term",
                    ),
                ),
                (
                    "experiment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.CASCADE,
                        to="animalv2.experiment",
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
            },
        ),
    ]
