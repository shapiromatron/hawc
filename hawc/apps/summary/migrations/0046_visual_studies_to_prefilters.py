# Generated by Django 4.2.3 on 2023-08-22 06:47

from django.db import migrations


def studies_prefilters(apps, schema_editor):
    # add studies field to prefilters
    Visual = apps.get_model("summary", "Visual")
    objs = Visual.objects.all().prefetch_related("studies")
    for obj in objs:
        # old logic was to use studies field if there were no prefilters
        # we preserve this here so that the visuals don't change
        if not any(value for value in obj.prefilters.values()):
            obj.prefilters["studies"] = list(obj.studies.all().values_list("pk", flat=True))
    Visual.objects.bulk_update(objs, ["prefilters"])


def reverse_studies_prefilters(apps, schema_editor):
    # separate studies field from prefilters
    Visual = apps.get_model("summary", "Visual")
    VisualStudy = Visual.studies.through
    objs = Visual.objects.all()
    m2m = []
    for obj in objs:
        studies = obj.prefilters.pop("studies", [])
        m2m.extend([VisualStudy(visual_id=obj.pk, study_id=study_id) for study_id in studies])
    Visual.objects.bulk_update(objs, ["prefilters"])
    VisualStudy.objects.bulk_create(m2m)


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0045_datapivotquery_published_only_to_prefilters"),
    ]

    operations = [
        migrations.RunPython(studies_prefilters, reverse_code=reverse_studies_prefilters),
        migrations.RemoveField(
            model_name="visual",
            name="studies",
        ),
    ]
