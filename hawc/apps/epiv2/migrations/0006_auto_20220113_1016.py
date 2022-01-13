# Generated by Django 3.2.10 on 2022-01-13 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epiv2', '0005_auto_20220113_1014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studypopulationv2',
            name='region',
            field=models.CharField(blank=True, default='', max_length=128, verbose_name='Other geographic information'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studypopulationv2',
            name='source',
            field=models.CharField(blank=True, choices=[('GP', 'General population'), ('OC', 'Occupational'), ('OT', 'Other')], default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studypopulationv2',
            name='study_design',
            field=models.CharField(blank=True, choices=[('CO', 'Cohort'), ('CC', 'Case-control'), ('NC', 'Nested case-control'), ('CR', 'Case report'), ('SE', 'Case series'), ('RT', 'Randomized controlled trial'), ('NT', 'Non-randomized controlled trial'), ('CS', 'Cross-sectional'), ('OT', 'Other')], default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studypopulationv2',
            name='years',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='Year(s) of data collection'),
            preserve_default=False,
        ),
    ]
