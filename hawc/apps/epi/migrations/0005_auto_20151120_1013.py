from django.db import migrations, models

"""
Original:
    (0, None),
    (1, "SD"),
    (2, "SEM"),
    (3, "GSD"),
    (4, "other"))

New:
    (0, None),
    (1, "SD"),
    (2, "SE"),
    (3, "SEM"),
    (4, "GSD"),
    (5, "other"))
"""


def update_variances(apps, schema_editor):
    Result = apps.get_model("epi", "Result")
    Result.objects.filter(variance_type=4).update(variance_type=5)
    Result.objects.filter(variance_type=3).update(variance_type=4)
    Result.objects.filter(variance_type=2).update(variance_type=3)


def revert_variances(apps, schema_editor):
    Result = apps.get_model("epi", "Result")
    Result.objects.filter(variance_type=3).update(variance_type=2)
    Result.objects.filter(variance_type=4).update(variance_type=3)
    Result.objects.filter(variance_type=5).update(variance_type=4)


class Migration(migrations.Migration):
    dependencies = [
        ("epi", "0004_auto_20151105_1056"),
    ]

    operations = [
        migrations.AlterField(
            model_name="result",
            name="variance_type",
            field=models.PositiveSmallIntegerField(
                default=0,
                choices=[
                    (0, None),
                    (1, b"SD"),
                    (2, b"SE"),
                    (3, b"SEM"),
                    (4, b"GSD"),
                    (5, b"other"),
                ],
            ),
        ),
        migrations.RunPython(update_variances, reverse_code=revert_variances),
    ]
