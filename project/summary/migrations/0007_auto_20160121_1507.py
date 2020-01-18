# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("summary", "0006_remove_datapivotquery_units"),
    ]

    operations = [
        migrations.RemoveField(model_name="datapivotquery", name="units",),
    ]
