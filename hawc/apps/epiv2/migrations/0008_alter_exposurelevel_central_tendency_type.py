# Generated by Django 3.2.10 on 2022-01-10 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epiv2', '0007_auto_20220110_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exposurelevel',
            name='central_tendency_type',
            field=models.CharField(blank=True, choices=[('MED', 'Median'), ('GME', 'Geometric Mean'), ('POI', 'Point'), ('MEA', 'Mean'), ('OTH', 'Other')], default='MED', max_length=128, null=True, verbose_name='Central tendency type (median preferred)'),
        ),
    ]
