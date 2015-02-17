# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.contenttypes.models import ContentType


def set_content_type(apps, schema_editor):
    StudyQuality = apps.get_model("study", "StudyQuality")
    Study = ContentType.objects.get(app_label="study", model="study")
    for sq in StudyQuality.objects.all():
        sq.content_type_id = Study.id
        sq.object_id = sq.study_id
        sq.save()

def set_study(apps, schema_editor):
    StudyQuality = apps.get_model("study", "StudyQuality")
    for sq in StudyQuality.objects.all():
        sq.study_id = sq.object_id
        sq.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('study', '0005_auto_20150209_2238'),
    ]

    operations = [
        migrations.AddField(
            model_name='studyquality',
            name='content_type',
            field=models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studyquality',
            name='object_id',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(set_content_type, reverse_code=set_study),
    ]
