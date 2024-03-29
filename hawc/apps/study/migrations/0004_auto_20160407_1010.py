# Generated by Django 1.9.4 on 2016-04-07 15:10


from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("study", "0003_studyquality_author"),
    ]

    database_operations = [
        migrations.AlterModelTable("StudyQualityDomain", "riskofbias_riskofbiasdomain"),
        migrations.AlterModelTable("StudyQualityMetric", "riskofbias_riskofbiasmetric"),
        migrations.AlterModelTable("StudyQuality", "riskofbias_riskofbias"),
    ]

    state_operations = [
        migrations.DeleteModel("StudyQualityDomain"),
        migrations.DeleteModel("StudyQualityMetric"),
        migrations.DeleteModel("StudyQuality"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations, state_operations=state_operations
        )
    ]
