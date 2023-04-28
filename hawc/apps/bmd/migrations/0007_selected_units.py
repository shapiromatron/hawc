import django.db.models.deletion
from django.db import migrations, models


def set_dose_units(apps, schema_editor):
    SelectedModel = apps.get_model("bmd", "selectedmodel")
    Session = apps.get_model("bmd", "session")
    updates = []
    for sm in SelectedModel.objects.all():
        if sm.model is None:
            sess = Session.objects.filter(endpoint_id=sm.endpoint_id).latest()
        else:
            sess = sm.model.session
        sm.dose_units_id = sess.dose_units_id
        updates.append(sm)
    SelectedModel.objects.bulk_update(updates, ["dose_units_id"])


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0018_auto_20160602_1007"),
        ("assessment", "0007_auto_20160426_1124"),
        ("bmd", "0006_django31"),
    ]

    operations = [
        migrations.AddField(
            model_name="selectedmodel",
            name="dose_units",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="selected_models",
                to="assessment.doseunits",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="selectedmodel",
            name="endpoint",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bmd_models",
                to="animal.endpoint",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="selectedmodel",
            unique_together={("endpoint", "dose_units")},
        ),
        migrations.RunPython(set_dose_units, migrations.RunPython.noop),
    ]
