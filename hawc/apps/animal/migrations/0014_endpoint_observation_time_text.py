from django.db import migrations, models


def setObservationTimeText(apps, schema_editor):
    Endpoint = apps.get_model("animal", "Endpoint")
    for ep in Endpoint.objects.all():
        txt = ""

        if ep.observation_time is None:
            txt = ep.get_observation_time_units_display()

        elif int(ep.observation_time) == float(ep.observation_time):
            txt = f"{int(ep.observation_time)} {ep.get_observation_time_units_display()}"

        else:
            txt = f"{ep.observation_time} {ep.get_observation_time_units_display()}"

        ep.observation_time_text = txt
        ep.save()


class Migration(migrations.Migration):
    dependencies = [
        ("animal", "0013_auto_20150924_1045"),
    ]

    operations = [
        migrations.AddField(
            model_name="endpoint",
            name="observation_time_text",
            field=models.CharField(
                help_text=b'Text for reported observation time (ex: "60-90 PND")',
                max_length=64,
                blank=True,
            ),
        ),
        migrations.RunPython(setObservationTimeText, reverse_code=migrations.RunPython.noop),
    ]
