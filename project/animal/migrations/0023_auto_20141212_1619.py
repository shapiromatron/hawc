# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def add_trend_result(apps, schema_editor):
    Endpoint = apps.get_model("animal", "Endpoint")
    Endpoint.objects.update(trend_result=3)
    Endpoint.objects.filter(trend_value__lte=0.05).update(trend_result=2)
    Endpoint.objects.filter(trend_value__gt=0.05).update(trend_result=1)
    Endpoint.objects.filter(monotonicity=0).update(trend_result=0)

def unadd_trend_result(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0022_auto_20141212_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='endpoint',
            name='trend_result',
            field=models.PositiveSmallIntegerField(default=3, choices=[(0, b'not applicable'), (1, b'not significant'), (2, b'significant'), (3, b'not reported')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dosingregime',
            name='route_of_exposure',
            field=models.CharField(max_length=2, choices=[(b'OC', 'Oral capsule'), (b'OD', 'Oral diet'), (b'OG', 'Oral gavage'), (b'OW', 'Oral drinking water'), (b'I', 'Inhalation'), (b'D', 'Dermal'), (b'SI', 'Subcutaneous injection'), (b'IP', 'Intraperitoneal injection'), (b'IO', 'in ovo'), (b'W', 'Whole body'), (b'U', 'Unknown'), (b'O', 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='monotonicity',
            field=models.PositiveSmallIntegerField(default=8, choices=[(0, b'N/A, single dose level study'), (1, b'N/A, no effects detected'), (2, b'yes, visual appearance of monotonicity but no trend'), (3, b'yes, monotonic and significant trend'), (4, b'yes, visual appearance of non-monotonic but no trend'), (5, b'yes, non-monotonic and significant trend'), (6, b'no pattern'), (7, b'unclear'), (8, b'not-reported')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='observation_time_units',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'not-reported'), (1, b'seconds'), (2, b'minutes'), (3, b'hours'), (4, b'days'), (5, b'weeks'), (6, b'months'), (7, b'PND'), (8, b'GD')]),
            preserve_default=True,
        ),
        migrations.RunPython(add_trend_result, reverse_code=unadd_trend_result),
    ]
