from django.db import migrations


def forward(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    changed = []
    for visual in Visual.objects.filter(visual_type=2):
        visual.settings["sort_order"] = visual.sort_order
        changed.append(visual)
    if changed:
        Visual.objects.bulk_update(changed, ["settings"])


def backward(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    changed = []
    for visual in Visual.objects.filter(visual_type=2):
        visual.sort_order = visual.settings.pop("sort_order")
        changed.append(visual)
    if changed:
        Visual.objects.bulk_update(changed, ["settings", "sort_order"])


class Migration(migrations.Migration):
    dependencies = [("summary", "0055_heatmap_count_column")]
    operations = [
        migrations.RunPython(forward, reverse_code=backward),
        migrations.RemoveField(model_name="visual", name="sort_order"),
    ]
