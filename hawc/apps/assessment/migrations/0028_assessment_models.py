import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("assessment", "0027_content_v2"),
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
    ]
