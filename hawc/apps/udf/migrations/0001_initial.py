import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserDefinedForm",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=128)),
                ("description", models.TextField()),
                ("schema", models.JSONField()),
                ("deprecated", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="udf_forms_creator",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "editors",
                    models.ManyToManyField(
                        blank=True, related_name="udf_forms", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="udf.userdefinedform",
                    ),
                ),
            ],
            options={
                "ordering": ("-last_updated",),
                "unique_together": {("creator", "name")},
            },
        ),
    ]
