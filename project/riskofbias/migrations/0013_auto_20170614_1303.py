# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-14 18:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("riskofbias", "0012_auto_20160608_1255"),
    ]

    operations = [
        migrations.RenameField(model_name="riskofbiasmetric", old_name="metric", new_name="name",),
    ]
