import json
from copy import deepcopy

import pandas as pd
from django.db import migrations

from hawc.apps.summary.constants import VisualType


def update_crossview(Visual):
    diff_data = []
    updates = []
    for v in Visual.objects.filter(visual_type=VisualType.BIOASSAY_CROSSVIEW):
        original_settings = deepcopy(v.settings)
        v.settings["refranges_dose"] = [
            d
            for d in v.settings["refranges_dose"]
            if d["lower"] is not None and d["upper"] is not None
        ]
        v.settings["refranges_response"] = [
            d
            for d in v.settings["refranges_response"]
            if d["lower"] is not None and d["upper"] is not None
        ]

        v.settings["reflines_dose"] = [
            d for d in v.settings["reflines_dose"] if d["value"] is not None
        ]
        v.settings["reflines_response"] = [
            d for d in v.settings["reflines_response"] if d["value"] is not None
        ]

        new_labels = []
        for lbl in v.settings["labels"]:
            if lbl["caption"]:
                lbl["x"] = lbl["x"] or 0
                lbl["y"] = lbl["y"] or 0
                lbl["max_width"] = lbl["max_width"] or 150
                new_labels.append(lbl)
        v.settings["labels"] = new_labels

        new_filters = []
        for filter in v.settings["filters"]:
            filter["x"] = filter["x"] or 0
            filter["y"] = filter["y"] or 0
            filter["values"] = filter["values"] or []
            filter["columns"] = filter["columns"] or 1
            new_filters.append(filter)
        v.settings["filters"] = new_filters

        diff_data.append((v.id, json.dumps(original_settings), json.dumps(v.settings)))
        updates.append(v)

    if updates:
        pd.DataFrame(data=diff_data, columns="id|old|new".split("|")).to_csv(
            "summary-migration-0061-crossview.csv", index=False
        )
        Visual.objects.bulk_update(updates, ["settings"])


def update_rob_barcharts(Visual):
    diff_data = []
    updates = []
    for v in Visual.objects.filter(visual_type=VisualType.ROB_BARCHART):
        original_settings = deepcopy(v.settings)

        if "show_nr_legend" not in v.settings:
            v.settings["show_nr_legend"] = True

            diff_data.append((v.id, json.dumps(original_settings), json.dumps(v.settings)))
            updates.append(v)

    if updates:
        pd.DataFrame(data=diff_data, columns="id|old|new".split("|")).to_csv(
            "summary-migration-0061-rob-barchart.csv", index=False
        )
        Visual.objects.bulk_update(updates, ["settings"])


def forward(apps, schema_editor):
    Visual = apps.get_model("summary", "Visual")
    update_crossview(Visual)
    update_rob_barcharts(Visual)


class Migration(migrations.Migration):
    dependencies = [("summary", "0060_delete_data_pivot")]
    operations = [migrations.RunPython(forward, reverse_code=migrations.RunPython.noop)]
