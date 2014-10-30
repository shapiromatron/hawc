# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitro', '0009_auto_20141027_1835'),
    ]

    operations = [
        migrations.CreateModel(
            name='IVEndpointCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=255)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        )
    ]
