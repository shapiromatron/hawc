# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0004_auto_20140929_1210'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(unique=True)),
                ('name', models.CharField(help_text=b'Adjective + noun combination', unique=True, max_length=128, verbose_name=b'Release name')),
                ('slug', models.SlugField(max_length=128, verbose_name=b'URL slug')),
                ('header', models.TextField(help_text=b'One-paragraph description of major changes made')),
                ('detailed_list', models.TextField(help_text=b'Detailed bulleted-list of individual item-changes')),
            ],
            options={
                'ordering': ('-date',),
            },
            bases=(models.Model,),
        ),
    ]
