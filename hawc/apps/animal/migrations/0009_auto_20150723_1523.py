from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("animal", "0008_auto_20150723_1252"), ("summary", "0001_initial")]

    database_operations = [
        migrations.AlterModelTable("Species", "assessment_species"),
        migrations.AlterModelTable("Strain", "assessment_strain"),
        migrations.AlterModelTable("DoseUnits", "assessment_doseunits"),
    ]

    operations = [migrations.SeparateDatabaseAndState(database_operations=database_operations)]
