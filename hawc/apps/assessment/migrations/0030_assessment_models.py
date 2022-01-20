import django.db.models.deletion
import pandas as pd
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models
from reversion.models import Version


def set_creator(apps, schema_editor):
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
                version.revision.user.id,
                version.object_id,
            ]
        )

    df = (
        pd.DataFrame(
            data=data, columns="log_id revision_timestamp revision_user_id assessment_id".split(" ")
        )
        .sort_values("revision_timestamp")
        .reset_index(drop=True)
    )

    if df.shape[0] == 0:
        return

    df["revision_timestamp"] = df["revision_timestamp"].dt.tz_localize(None)
    df.assessment_id = df.assessment_id.astype(int)

    df = (
        df.groupby("assessment_id").nth(0)[["revision_timestamp", "revision_user_id"]].reset_index()
    )

    dict = pd.Series(data=df.revision_user_id, index=df.assessment_id).to_dict()

    Assessment = apps.get_model("assessment", "assessment")
    updates = []
    for assessment in Assessment.objects.all():
        user_id = dict.get(assessment.id)
        if user_id:
            assessment.creator_id = user_id
            updates.append(assessment)

    Assessment.objects.bulk_update(updates, ["creator_id"])


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
                verbose_name="Assessment authors",
                help_text="""A public description of the assessment authors. If this assessment is
        made public, this will be shown to describe the authors of this project.""",
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
                help_text="Describe the assessment objective(s), research questions, or clarification on the purpose of the assessment."
            ),
        ),
        migrations.AlterField(
            model_name="assessment",
            name="is_public_training_data",
            field=models.BooleanField(
                default=True,
                help_text="Allows data to be anonymized and made available for machine learning projects. Both assessment ID and user ID will be made anonymous for these purposes.",
                verbose_name="Public training data",
            ),
        ),
        migrations.RunPython(set_creator, migrations.RunPython.noop),
    ]
