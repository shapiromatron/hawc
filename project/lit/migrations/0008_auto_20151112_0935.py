# -*- coding: utf-8 -*-


from django.db import migrations, models
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ("lit", "0007_auto_20151103_0925"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reference",
            name="full_text_url",
            field=utils.models.CustomURLField(
                help_text=b"Link to full-text publication (may require increased access privileges, only reviewers and team-members)",
                blank=True,
            ),
        ),
    ]
