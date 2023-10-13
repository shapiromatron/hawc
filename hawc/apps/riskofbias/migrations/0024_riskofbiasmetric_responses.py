from django.conf import settings
from django.db import migrations, models

from ..constants import RiskOfBiasResponses


def set_default_responses(apps, schema_editor):
    # update metric settings
    RiskOfBiasMetric = apps.get_model("riskofbias", "RiskOfBiasMetric")
    if settings.HAWC_FLAVOR == "PRIME":
        RiskOfBiasMetric.objects.update(responses=RiskOfBiasResponses.HIGH_LOW_BIAS)
    elif settings.HAWC_FLAVOR == "EPA":
        RiskOfBiasMetric.objects.filter(domain__is_overall_confidence=False).update(
            responses=RiskOfBiasResponses.GOOD_DEFICIENT
        )
        RiskOfBiasMetric.objects.filter(domain__is_overall_confidence=True).update(
            responses=RiskOfBiasResponses.HIGH_LOW_CONFIDENCE
        )
    else:
        raise ValueError("Unknown HAWC flavor")


class Migration(migrations.Migration):
    dependencies = [
        ("riskofbias", "0023_sort_order"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="riskofbiasassessment",
            name="default_questions",
        ),
        migrations.RemoveField(
            model_name="riskofbiasassessment",
            name="responses",
        ),
        migrations.AddField(
            model_name="riskofbiasmetric",
            name="responses",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "None"),
                    (1, "High/Low risk of bias"),
                    (2, "Good/deficient"),
                    (3, "High/low confidence"),
                    (4, "Yes/No"),
                    (5, "Minor/Critical concerns"),
                    (6, "Minor/Critical concerns (sensitivity)"),
                ],
                default=999,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_responses, reverse_code=migrations.RunPython.noop),
    ]
