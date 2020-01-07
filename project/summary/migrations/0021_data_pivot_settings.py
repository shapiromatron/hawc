# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-07 17:13
from __future__ import unicode_literals

from copy import copy
import json
from pathlib import Path

from django.db import migrations
from django.conf import settings

from assessment.models import NOEL_NAME_CHOICES_NOEL
from summary import models


def _replace_column(text: str, existing: str, replacement: str) -> str:

    return (
        text
        .replace(f'"low_field_name":"{existing}"', f'"low_field_name":"{replacement}"')
        .replace(f'"low_field_name": "{existing}"', f'"low_field_name":"{replacement}"')
        .replace(f'"high_field_name":"{existing}"', f'"high_field_name":"{replacement}"')
        .replace(f'"high_field_name": "{existing}"', f'"high_field_name":"{replacement}"')
        .replace(f'"field_name":"{existing}"', f'"field_name":"{replacement}"')
        .replace(f'"field_name": "{existing}"', f'"field_name":"{replacement}"')
        .replace(f'"error_low_field_name":"{existing}"', f'"error_low_field_name":"{replacement}"')
        .replace(f'"error_low_field_name": "{existing}"', f'"error_low_field_name":"{replacement}"')
        .replace(f'"error_high_field_name":"{existing}"', f'"error_high_field_name":"{replacement}"')
        .replace(f'"error_high_field_name": "{existing}"', f'"error_high_field_name":"{replacement}"')
    )


def rename_fields(apps, schema_editor):
    if settings.HAWC_FLAVOR != "EPA":
        return

    changes = []
    DataPivotQuery = apps.get_model('summary', 'DataPivotQuery')

    # bioassay
    for obj in DataPivotQuery.objects.filter(evidence_type=models.BIOASSAY, export_style=0):
        old_settings = copy(obj.settings)
        new_settings = copy(obj.settings)

        if obj.assessment.noel_name == NOEL_NAME_CHOICES_NOEL:
            new_settings = _replace_column(new_settings, 'LOAEL', 'LOEL')
            new_settings = _replace_column(new_settings, 'NOAEL', 'NOEL')

        if new_settings != old_settings:
            print(f'Updating data pivot -> animal endpoint group: {obj.id}')
            obj.settings = new_settings
            obj.save()
            changes.append(dict(id=obj.id, old=old_settings, new=new_settings))

    for obj in DataPivotQuery.objects.filter(evidence_type=models.BIOASSAY, export_style=1):
        old_settings = copy(obj.settings)
        new_settings = copy(obj.settings)

        if obj.assessment.noel_name == NOEL_NAME_CHOICES_NOEL:
            new_settings = _replace_column(new_settings, 'LOAEL', 'LOEL')
            new_settings = _replace_column(new_settings, 'NOAEL', 'NOEL')

        if new_settings != old_settings:
            print(f'Updating data pivot -> animal endpoint: {obj.id}')
            obj.settings = new_settings
            obj.save()
            changes.append(dict(id=obj.id, old=old_settings, new=new_settings))

    for obj in DataPivotQuery.objects.filter(evidence_type=models.EPI):
        old_settings = copy(obj.settings)
        new_settings = copy(obj.settings)

        new_settings = _replace_column(new_settings, 'estimate type', "exposure estimate type")
        new_settings = _replace_column(new_settings, 'estimate', "exposure estimate")
        new_settings = _replace_column(new_settings, 'variance type', "exposure variance type")
        new_settings = _replace_column(new_settings, 'variance', "exposure variance")
        new_settings = _replace_column(new_settings, 'lower bound interval', "exposure lower bound interval")
        new_settings = _replace_column(new_settings, 'upper bound interval', "exposure upper bound interval")
        new_settings = _replace_column(new_settings, 'lower CI', "exposure lower ci")
        new_settings = _replace_column(new_settings, 'upper CI', "exposure upper ci")
        new_settings = _replace_column(new_settings, 'lower range', "exposure lower range")
        new_settings = _replace_column(new_settings, 'upper range', "exposure upper range")

        new_settings = _replace_column(new_settings, 'group estimate', 'estimate')
        new_settings = _replace_column(new_settings, 'group lower ci', 'lower CI')
        new_settings = _replace_column(new_settings, 'group upper ci', 'upper CI')
        new_settings = _replace_column(new_settings, 'group lower range', 'lower range')
        new_settings = _replace_column(new_settings, 'group upper range', 'upper range')
        new_settings = _replace_column(new_settings, 'group lower bound interval', 'lower bound interval')
        new_settings = _replace_column(new_settings, 'group upper bound interval', 'upper bound interval')
        new_settings = _replace_column(new_settings, 'group variance', 'variance')

        if new_settings != old_settings:
            print(f'Updating data pivot -> epi: {obj.id}')
            obj.settings = new_settings
            obj.save()
            changes.append(dict(id=obj.id, old=old_settings, new=new_settings))

    Path('0021_data_pivot_settings.json').write_text(json.dumps(changes))


class Migration(migrations.Migration):

    dependencies = [
        ('summary', '0020_auto_20190407_2040'),
    ]

    operations = [
        migrations.RunPython(rename_fields),
    ]
