# Generated by Django 1.11.9 on 2018-02-23 20:48

from django.db import migrations, models


def updateAssessmentVersion(apps, schema_editor):
    Assessment = apps.get_model("assessment", "Assessment")
    AssessmentSettings = apps.get_model("bmd", "assessmentsettings")
    Session = apps.get_model("bmd", "session")
    ids = []
    for assessment in Assessment.objects.all():
        sessions = Session.objects.filter(endpoint__assessment=assessment).count()
        if sessions == 0:
            ids.append(assessment.id)

    AssessmentSettings.objects.filter(assessment_id__in=ids).update(version="BMDS270")


class Migration(migrations.Migration):
    dependencies = [
        ("bmd", "0003_auto_20160722_1318"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessmentsettings",
            name="version",
            field=models.CharField(
                choices=[
                    ("BMDS231", "BMDS v2.3.1"),
                    ("BMDS240", "BMDS v2.4.0"),
                    ("BMDS260", "BMDS v2.6.0"),
                    ("BMDS2601", "BMDS v2.6.0.1"),
                    ("BMDS270", "BMDS v2.7.0"),
                ],
                default="BMDS270",
                max_length=10,
            ),
        ),
        migrations.RunPython(updateAssessmentVersion, reverse_code=migrations.RunPython.noop),
    ]
