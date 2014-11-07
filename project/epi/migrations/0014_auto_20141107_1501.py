# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_metric_abbreviations(apps, schema_editor):

    abbrev_cw = {
        "not reported": "",
        "adjusted relative risk": "adjRR",
        "relative risk": "RR",
        "adjusted prevalence ratio": "adjPR",
        "prevalence ratio": "PR",
        "adjusted hazard ratio": "adjHR",
        "hazard ratio": "HR",
        "adjusted beta": "adjβ",
        "crude odds ratio": "OR",
        "adjusted odds ratio": "adjOR",
        "correlation": "r",
    }

    StatisticalMetric = apps.get_model("epi", "StatisticalMetric")
    for metric in StatisticalMetric.objects.all():
        name = metric.metric
        metric.abbreviation = abbrev_cw.get(name, name[:31])
        metric.save()

class Migration(migrations.Migration):

    dependencies = [
        ('epi', '0013_statisticalmetric_abbreviation'),
    ]

    operations = [
        migrations.RunPython(add_metric_abbreviations),
    ]
