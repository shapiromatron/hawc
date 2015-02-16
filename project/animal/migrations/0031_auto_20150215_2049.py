# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_litter_effects(apps, schema_editor):
    Experiment = apps.get_model("animal", "Experiment")
    Experiment.objects.update(litter_effects="NA")
    Experiment.objects\
        .filter(type__in=["Rp", "Dv"])\
        .update(litter_effects="NR")

def unadd_litter_effects(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0030_auto_20150211_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='animal_source',
            field=models.CharField(help_text=b'Laboratory and/or breeding details where animals were acquired', max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='diet',
            field=models.CharField(help_text=b'Description of animal-feed, if relevant', max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='litter_effect_notes',
            field=models.CharField(help_text=b'Any additional notes describing how litter effects were controlled', max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='experiment',
            name='litter_effects',
            field=models.CharField(default=b'NA', help_text=b'Type of controls used for litter-effects', max_length=2, choices=[(b'NA', b'Not-applicable'), (b'NR', b'Not-reported'), (b'YS', b'Yes, statistical controls'), (b'YD', b'Yes, study-design'), (b'N', b'No'), (b'O', b'Other')]),
            preserve_default=True,
        ),
        migrations.RunPython(add_litter_effects, reverse_code=unadd_litter_effects),
    ]
