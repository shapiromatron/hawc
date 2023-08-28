# Generated by Django 4.2.3 on 2023-08-21 03:49
import json

from django.db import migrations, models

from hawc.apps.summary.prefilters import StudyTypePrefilter

mapping = {
    StudyTypePrefilter.BIOASSAY:{
        "published_only":"animal_group__experiment__study__published",
        "studies":"animal_group__experiment__study__in",
        "systems":"system__in",
        "organs":"organ__in",
        "effects":"effect__in",
        "effect_subtypes":"effect_subtype__in",
        "effect_tags":"effects__in"
    },
    StudyTypePrefilter.EPIV1:{
        "published_only":"study_population__study__published",
        "studies":"study_population__study__in",
        "systems":"system__in",
        "effects":"effect__in",
        "effect_tags":"effects__in"
    },
    StudyTypePrefilter.EPIV2:{
        "published_only":"design__study__published",
        "studies":"design__study__in"
    },
    StudyTypePrefilter.EPI_META:{
        "published_only":"protocol__study__published",
        "studies":"protocol__study__in"
    },
    StudyTypePrefilter.IN_VITRO:{
        "published_only":"experiment__study__published",
        "studies":"experiment__study__in",
        "categories":"category__in",
        "chemicals":"chemical__name__in",
        "effect_tags":"effects__in"
    },
    StudyTypePrefilter.ECO:{
        "published_only":"design__study__published",
        "studies":"design__study__in"
    }
}

def prefilters_dict(apps, schema_editor):
    # load prefilters textfield into temp jsonfield
    DataPivotQuery = apps.get_model("summary", "DataPivotQuery")
    objs = DataPivotQuery.objects.all().select_related("assessment")
    for obj in objs:
        data = json.loads(obj.prefilters)
        if not data:
            continue
        key_map = mapping[StudyTypePrefilter.from_study_type(obj.evidence_type,obj.assessment)]
        key_map = {v:k for k,v in key_map.items()}
        data = {key_map[k]:v for k,v in data.items()}
        obj.temp = data
    DataPivotQuery.objects.bulk_update(objs, ["temp"])


def reverse_prefilters_dict(apps, schema_editor):
    # dump temp jsonfield into prefilters textfield
    DataPivotQuery = apps.get_model("summary", "DataPivotQuery")
    objs = DataPivotQuery.objects.all().select_related("assessment")
    for obj in objs:
        if not obj.temp:
            continue
        key_map = mapping[StudyTypePrefilter.from_study_type(obj.evidence_type,obj.assessment)]
        data = {key_map[k]:v for k,v in obj.temp.items()}
        obj.prefilters = json.dumps(data)
    DataPivotQuery.objects.bulk_update(objs, ["prefilters"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0042_summarytable_interactive"),
    ]

    operations = [
        # change prefilters textfield into jsonfield
        migrations.AddField(
            model_name="datapivotquery",
            name="temp",
            field=models.JSONField(default=dict),
        ),
        migrations.RunPython(prefilters_dict, reverse_code=reverse_prefilters_dict),
        migrations.RemoveField(
            model_name="datapivotquery",
            name="prefilters",
        ),
        migrations.RenameField(
            model_name="datapivotquery",
            old_name="temp",
            new_name="prefilters",
        ),
    ]
