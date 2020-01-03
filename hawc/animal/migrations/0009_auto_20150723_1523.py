# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0008_auto_20150723_1252'),
    ]

    database_operations = [
        migrations.AlterModelTable('Species', 'assessment_species'),
        migrations.AlterModelTable('Strain', 'assessment_strain'),
        migrations.AlterModelTable('DoseUnits', 'assessment_doseunits'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations)
    ]
