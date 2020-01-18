# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("epimeta", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="singleresult", options={"ordering": ("exposure_name",)},
        ),
    ]
