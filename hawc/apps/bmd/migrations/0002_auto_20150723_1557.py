from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bmd", "0001_initial"),
        ("animal", "0010_auto_20150723_1536"),
    ]

    state_operations = [
        migrations.AlterField(
            model_name="bmd_session",
            name="dose_units",
            field=models.ForeignKey(to="assessment.DoseUnits", on_delete=models.CASCADE),
        ),
    ]

    operations = [migrations.SeparateDatabaseAndState(state_operations=state_operations)]
