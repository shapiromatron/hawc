from django.db import migrations


def forwards(apps, schema_editor):
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        if "plot_settings" not in dp.settings:
            continue
        dp.settings["plot_settings"].update(
            x_axis_number_ticks=10,
            x_axis_force_domain=False,
            text_background_extend=False,
            draw_background=True,
            plot_background_color="#EEEEEE",
            draw_gridlines=True,
            gridline_color="#FFFFFF",
            draw_plot_border=True,
            plot_border_color="#666666",
        )
        updates.append(dp)
    if updates:
        DataPivot.objects.bulk_update(updates, ["settings"])


def backwards(apps, schema_editor):
    updates = []
    DataPivot = apps.get_model("summary", "DataPivot")
    for dp in DataPivot.objects.all():
        if "plot_settings" not in dp.settings:
            continue
        for field in [
            "x_axis_number_ticks",
            "x_axis_force_domain",
            "text_background_extend",
            "draw_background",
            "plot_background_color",
            "draw_gridlines",
            "gridline_color",
            "draw_plot_border",
            "plot_border_color",
        ]:
            dp.settings["plot_settings"].pop(field, None)
        updates.append(dp)
    if updates:
        DataPivot.objects.bulk_update(updates, ["settings"])


class Migration(migrations.Migration):
    dependencies = [
        ("summary", "0043_alter_datapivot_settings"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=backwards),
    ]
