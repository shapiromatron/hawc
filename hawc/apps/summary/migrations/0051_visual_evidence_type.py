# Generated by Django 4.2.3 on 2023-10-24 16:32

from django.db import migrations, models

from hawc.apps.summary.constants import get_default_evidence_type


def set_defaults(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    objs = Visual.objects.all()
    updated_objs = []
    for obj in objs:
        # if theres a default evidence_type, use it
        try:
            evidence_type = get_default_evidence_type(obj.visual_type)
            obj.evidence_type = evidence_type
        # otherwise assume bioassay remains the default
        except ValueError:
            pass
        if obj.evidence_type != 0:
            updated_objs.append(obj)
    Visual.objects.bulk_update(updated_objs, ["evidence_type"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0050_heatmap_counts"),
    ]

    operations = [
        migrations.AddField(
            model_name="visual",
            name="evidence_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Animal Bioassay"),
                    (1, "Epidemiology"),
                    (4, "Epidemiology meta-analysis/pooled analysis"),
                    (2, "In vitro"),
                    (5, "Ecology"),
                    (3, "Other"),
                ],
                default=0,
            ),
        ),
        migrations.RunPython(set_defaults, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="visual",
            name="evidence_type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Animal Bioassay"),
                    (1, "Epidemiology"),
                    (4, "Epidemiology meta-analysis/pooled analysis"),
                    (2, "In vitro"),
                    (5, "Ecology"),
                    (3, "Other"),
                ]
            ),
        ),
    ]
