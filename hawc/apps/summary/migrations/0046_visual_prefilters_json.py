# Generated by Django 4.2.3 on 2023-08-21 03:49
import json

from django.db import migrations, models

key_map = {
    "published_only": "animal_group__experiment__study__published",
    "studies": "animal_group__experiment__study__in",
    "systems": "system__in",
    "organs": "organ__in",
    "effects": "effect__in",
    "effect_subtypes": "effect_subtype__in",
    "effect_tags": "effects__in",
}


def prefilters_dict(apps, schema_editor):
    # load prefilters textfield into temp jsonfield
    Visual = apps.get_model("summary", "Visual")
    objs = Visual.objects.all()
    for obj in objs:
        data = json.loads(obj.prefilters)
        if not data:
            continue
        reverse_key_map = {v: k for k, v in key_map.items()}
        data = {reverse_key_map[k]: v for k, v in data.items() if v}
        obj.temp = data
    Visual.objects.bulk_update(objs, ["temp"])


def reverse_prefilters_dict(apps, schema_editor):
    # dump temp jsonfield into prefilters textfield
    Visual = apps.get_model("summary", "Visual")
    objs = Visual.objects.all()
    for obj in objs:
        if not obj.temp:
            continue
        data = {key_map[k]: v for k, v in obj.temp.items()}
        obj.prefilters = json.dumps(data)
    Visual.objects.bulk_update(objs, ["prefilters"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0045_datapivotquery_prefilters_json"),
    ]

    operations = [
        # change prefilters textfield into jsonfield
        migrations.AddField(
            model_name="visual",
            name="temp",
            field=models.JSONField(default=dict),
        ),
        migrations.RunPython(prefilters_dict, reverse_code=reverse_prefilters_dict),
        migrations.RemoveField(
            model_name="visual",
            name="prefilters",
        ),
        migrations.RenameField(
            model_name="visual",
            old_name="temp",
            new_name="prefilters",
        ),
    ]
