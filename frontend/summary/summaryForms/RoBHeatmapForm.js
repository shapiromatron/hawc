import _ from "lodash";
import {DEFAULT} from "shared/constants";
import RoBHeatmap from "summary/summary/RoBHeatmap";

import $ from "$";

import BaseVisualForm from "./BaseVisualForm";
import {CheckboxField, IntegerField, SelectField, TextField} from "./Fields";
import RoBMetricTable from "./RoBMetricTable";
import RoBScoreExcludeTable from "./RoBScoreExcludeTable";

class RoBHeatmapForm extends BaseVisualForm {
    afterGetDataHook(data) {
        RoBHeatmap.transformData(data);
    }

    buildPreview($parent, data) {
        this.preview = new RoBHeatmap(data).displayAsPage($parent.empty(), {dev: true});
    }

    initDataForm() {
        ["system", "organ", "effect", "effect_subtype"].forEach(d => {
            $(`#id_prefilter_${d}`)
                .on("change", function () {
                    var div = $(`#div_id_${d}s`);
                    $(this).prop("checked") ? div.show(1000) : div.hide(0);
                })
                .trigger("change");
        });
    }

    updateSettingsFromPreview() {
        var plotSettings = JSON.stringify(this.preview.data.settings);
        $("#id_settings").val(plotSettings);
        this.unpackSettings();
    }
}

_.extend(RoBHeatmapForm, {
    tabs: [
        {name: "overall", label: "General settings"},
        {name: "metrics", label: "Included metrics"},
        {name: "excluded_scores", label: "Included judgments"},
        {name: "legend", label: "Legend settings"},
    ],
    schema: [
        {
            type: TextField,
            name: "title",
            label: "Title",
            def: "",
            tab: "overall",
        },
        {
            type: TextField,
            name: "xAxisLabel",
            label: "X-axis label",
            def: "",
            tab: "overall",
        },
        {
            type: TextField,
            name: "yAxisLabel",
            label: "Y-axis label",
            def: "",
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_top",
            label: "Plot padding-top (px)",
            def: 20,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "cell_size",
            label: "Cell-size (px)",
            def: 40,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_right",
            label: "Plot padding-right (px)",
            def: 330,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_bottom",
            label: "Plot padding-bottom (px)",
            def: 35,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_left",
            label: "Plot padding-left (px)",
            def: 20,
            tab: "overall",
        },
        {
            type: SelectField,
            name: "x_field",
            label: "X-axis field",
            opts: [
                ["study", "Study"],
                ["metric", "RoB metric"],
            ],
            def: "study",
            tab: "overall",
        },
        {
            type: SelectField,
            name: "study_label_field",
            label: "Study label",
            opts: [
                ["short_citation", "Short citation"],
                ["study_identifier", "Study identifier"],
            ],
            def: "short_citation",
            tab: "overall",
            helpText: "Label to show on the axis to describe each study.",
        },
        {
            type: RoBMetricTable,
            prependSpacer: false,
            label: "Included metrics",
            name: "included_metrics",
            colWidths: [10, 90],
            addBlankRowIfNone: false,
            tab: "metrics",
        },
        {
            type: RoBScoreExcludeTable,
            prependSpacer: false,
            label: "Included judgments",
            name: "excluded_score_ids",
            colWidths: [10, 30, 30, 30],
            addBlankRowIfNone: false,
            tab: "excluded_scores",
        },
        {
            type: CheckboxField,
            name: "show_legend",
            label: "Show legend",
            def: true,
            tab: "legend",
        },
        {
            type: CheckboxField,
            name: "show_na_legend",
            label: "Show N/A in legend",
            def: true,
            helpText: 'Show "Not applicable" in the legend',
            tab: "legend",
        },
        {
            type: CheckboxField,
            name: "show_nr_legend",
            label: "Show NR in legend",
            def: true,
            helpText: 'Show "Not reported" in the legend',
            tab: "legend",
        },
        {
            type: IntegerField,
            name: "legend_x",
            label: "Legend x-location (px)",
            def: DEFAULT,
            helpText: `Absolute legend location; for default set to ${DEFAULT}`,
            tab: "legend",
        },
        {
            type: IntegerField,
            name: "legend_y",
            label: "Legend y-location (px)",
            def: DEFAULT,
            helpText: `Absolute legend location; for default set to ${DEFAULT}`,
            tab: "legend",
        },
    ],
});

export default RoBHeatmapForm;
