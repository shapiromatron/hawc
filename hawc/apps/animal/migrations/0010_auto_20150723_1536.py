from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0009_auto_20150723_1523"),
        ("assessment", "0004_auto_20150723_1530"),
    ]

    state_operations = [
        migrations.AlterField(
            model_name="animalgroup",
            name="species",
            field=models.ForeignKey(to="assessment.Species", on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name="animalgroup",
            name="strain",
            field=models.ForeignKey(to="assessment.Strain", on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name="dosegroup",
            name="dose_units",
            field=models.ForeignKey(to="assessment.DoseUnits", on_delete=models.CASCADE),
        ),
    ]

    operations = [migrations.SeparateDatabaseAndState(state_operations=state_operations)]
