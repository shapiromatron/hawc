# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0002_auto_20150629_1211'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animalgroup',
            name='parents',
            field=models.ManyToManyField(related_name='children', to='animal.AnimalGroup', blank=True),
        ),
    ]
