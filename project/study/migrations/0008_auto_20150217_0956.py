# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('study', '0007_auto_20150217_0930'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studyquality',
            options={'ordering': ('content_type', 'object_id', 'metric'), 'verbose_name_plural': 'Study Qualities'},
        ),
        migrations.AlterField(
            model_name='studyquality',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studyquality',
            name='object_id',
            field=models.PositiveIntegerField(),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='studyquality',
            unique_together=set([('content_type', 'object_id', 'metric')]),
        ),
        migrations.RemoveField(
            model_name='studyquality',
            name='study',
        ),
    ]
