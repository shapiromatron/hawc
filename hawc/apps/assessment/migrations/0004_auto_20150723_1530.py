from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0003_remove_assessment_enable_reference_values"),
        ("animal", "0009_auto_20150723_1523"),
    ]

    state_operations = [
        migrations.CreateModel(
            name="DoseUnits",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("units", models.CharField(unique=True, max_length=20)),
                ("administered", models.BooleanField(default=False)),
                ("converted", models.BooleanField(default=False)),
                (
                    "hed",
                    models.BooleanField(default=False, verbose_name=b"Human Equivalent Dose"),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name_plural": "dose units"},
        ),
        migrations.CreateModel(
            name="Species",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text=b"Enter species in singular (ex: Mouse, not Mice)",
                        unique=True,
                        max_length=30,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ("name",), "verbose_name_plural": "species"},
        ),
        migrations.CreateModel(
            name="Strain",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("name", models.CharField(max_length=30)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("species", models.ForeignKey(to="assessment.Species", on_delete=models.CASCADE)),
            ],
            options={"ordering": ("species", "name")},
        ),
    ]

    operations = [migrations.SeparateDatabaseAndState(state_operations=state_operations)]
