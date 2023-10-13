from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assessment", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assessment",
            name="reviewers",
            field=models.ManyToManyField(
                help_text=b"Can view the assessment even if the assessment is not public, but cannot add or change content. Reviewers may optionally add comments, if this feature is enabled. You can add multiple reviewers.",
                related_name="assessment_reviewers",
                to=settings.AUTH_USER_MODEL,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="assessment",
            name="team_members",
            field=models.ManyToManyField(
                help_text=b"Can view and edit assessment components, if project is editable. You can add multiple team-members",
                related_name="assessment_teams",
                to=settings.AUTH_USER_MODEL,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="baseendpoint",
            name="effects",
            field=models.ManyToManyField(
                to="assessment.EffectTag", verbose_name=b"Tags", blank=True
            ),
        ),
    ]
