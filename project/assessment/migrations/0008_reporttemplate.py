# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0007_auto_20141104_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=256)),
                ('report_type', models.PositiveSmallIntegerField(choices=[(0, b'Literature search'), (1, b'Studies and study-quality'), (2, b'Animal bioassay'), (3, b'Epidemiology'), (4, b'Epidemiology meta-analysis/pooled analysis'), (5, b'In vitro')])),
                ('template', models.FileField(upload_to=b'templates')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('assessment', models.ForeignKey(related_name='templates', blank=True, to='assessment.Assessment', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
