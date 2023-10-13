import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("assessment", "0027_content_v2"),
    ]

    operations = [
        migrations.AddField(
            model_name="log",
            name="content",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="log",
            name="content_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AddField(
            model_name="log",
            name="object_id",
            field=models.IntegerField(null=True),
        ),
        migrations.RemoveField(model_name="log", name="last_updated"),
    ]
