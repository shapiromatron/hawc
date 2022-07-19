from django.db import migrations

from ..constants import NR_SCORES


def forwards_func(apps, schema_editor):
    RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")
    RiskOfBiasScore.objects.filter(score__in=NR_SCORES, notes="<p> </p>").update(notes="<p>-</p>")


def reverse_func(apps, schema_editor):
    RiskOfBiasScore = apps.get_model("riskofbias", "RiskOfBiasScore")
    RiskOfBiasScore.objects.filter(score__in=NR_SCORES, notes="<p>-</p>").update(notes="<p> </p>")


class Migration(migrations.Migration):
    dependencies = [("riskofbias", "0025_alter_riskofbias_study")]
    operations = [migrations.RunPython(forwards_func, reverse_code=reverse_func)]
