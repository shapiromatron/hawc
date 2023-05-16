import json

import django.db.models.deletion
import pandas as pd
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models
from django.utils import timezone
from reversion.models import Version


def set_creator(apps, schema_editor):
    Assessment = apps.get_model("assessment", "assessment")

    # end early if there are no assessments / fresh db
    # https://stackoverflow.com/questions/40344994/
    if Assessment.objects.count() == 0:
        return

    ct_id = ContentType.objects.get(app_label="assessment", model="assessment").id
    versions = Version.objects.filter(content_type=ct_id).select_related(
        "revision", "revision__user"
    )
    data = []
    for version in versions:
        data.append(
            [
                version.id,
                version.revision.date_created,
                version.revision.user.id if version.revision.user else None,
                version.object_id,
            ]
        )

    df = (
        pd.DataFrame(
            data=data, columns="log_id revision_timestamp revision_user_id assessment_id".split(" ")
        )
        .sort_values("revision_timestamp")
        .reset_index(drop=True)
        .dropna()
    )

    if df.shape[0] == 0:
        return

    df["revision_timestamp"] = df["revision_timestamp"].dt.tz_localize(None)
    df.assessment_id = df.assessment_id.astype(int)
    df.revision_user_id = df.revision_user_id.astype(int)
    df = (
        df.groupby("assessment_id").nth(0)[["revision_timestamp", "revision_user_id"]].reset_index()
    )

    dict = pd.Series(data=df.revision_user_id.values, index=df.assessment_id).to_dict()
    updates = []
    for assessment in Assessment.objects.all():
        user_id = dict.get(assessment.id)
        if user_id:
            assessment.creator_id = user_id
            updates.append(assessment)

    Assessment.objects.bulk_update(updates, ["creator_id"])


def set_public_on(apps, schema_editor):
    Assessment = apps.get_model("assessment", "assessment")

    # end early if there are no assessments / fresh db
    # https://stackoverflow.com/questions/40344994/
    if Assessment.objects.count() == 0:
        return

    ct_id = ContentType.objects.get(app_label="assessment", model="assessment").id

    versions = Version.objects.filter(content_type=ct_id).select_related("revision")

    data = []
    for version in versions:
        log = json.loads(version.serialized_data)
        public = log[0].get("fields").get("public")
        if public:
            data.append([version.id, version.revision.date_created, version.object_id, public])

    df = (
        pd.DataFrame(data=data, columns="log_id revision_timestamp assessment_id public".split(" "))
        .sort_values("revision_timestamp")
        .reset_index(drop=True)
    )

    if df.shape[0] == 0:
        return

    df.assessment_id = df.assessment_id.astype(int)

    df2 = df.groupby("assessment_id").nth(0)[["revision_timestamp"]].reset_index()

    timestamps = pd.Series(
        data=df2.revision_timestamp.values, index=df2.assessment_id
    ).dt.tz_localize("utc")

    updates = []
    # set the public_on date for all public assessments
    for assessment in Assessment.objects.filter(public=True):
        release_dt = timestamps.get(assessment.id)
        if release_dt:
            assessment.public_on = release_dt
        else:
            # if a date was not found, set public_on to now
            assessment.public_on = timezone.now()
        updates.append(assessment)

    Assessment.objects.bulk_update(updates, ["public_on"])


def unset_public_on(apps, schema_editor):
    Assessment = apps.get_model("assessment", "assessment")
    Assessment.objects.filter(public_on__isnull=False).update(public=True)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("assessment", "0029_communication"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="authors",
            field=models.TextField(
                default="",
                verbose_name="Assessment authors/organization",
                help_text="""A publicly visible description of the assessment authors (if the assessment is made public). This could be an organization, a group, or the individual scientists involved.""",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="assessment",
            name="creator",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_assessments",
                to=settings.AUTH_USER_MODEL,
                editable=False,
            ),
        ),
        migrations.AlterField(
            model_name="assessment",
            name="assessment_objective",
            field=models.TextField(
                help_text="Describe the assessment objective(s), research questions, and purpose of this HAWC assessment. If a related peer-reviewed paper or journal article is available describing this work, please add a citation and hyperlink.",
            ),
        ),
        migrations.AddField(
            model_name="assessment",
            name="public_on",
            field=models.DateTimeField(
                blank=True,
                help_text="The assessment can be viewed by the general public.",
                null=True,
                verbose_name="Public",
            ),
        ),
        migrations.RunPython(set_public_on, unset_public_on),
        migrations.RunPython(set_creator, migrations.RunPython.noop),
    ]
