from django.db import migrations

from ..sql import FinalRiskOfBiasScore


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("riskofbias", "0022_new_rob_scores"),
    ]

    operations = [migrations.RunSQL(FinalRiskOfBiasScore.create, FinalRiskOfBiasScore.drop,)]
