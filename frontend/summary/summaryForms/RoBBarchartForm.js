import _ from "lodash";

import RoBBarchart from "summary/summary/RoBBarchart";

import RoBHeatmapForm from "./RoBHeatmapForm";
import RoBMetricTable from "./RoBMetricTable";
import RoBScoreExcludeTable from "./RoBScoreExcludeTable";
import {TextField, IntegerField, CheckboxField} from "./Fields";

class RoBBarchartForm extends RoBHeatmapForm {
    buildPreview($parent, data) {
        this.preview = new RoBBarchart(data).displayAsPage($parent.empty(), {
            dev: true,
        });
    }
}

_.extend(RoBBarchartForm, {
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
            def: "Title",
            tab: "overall",
        },
        {
            type: TextField,
            name: "xAxisLabel",
            label: "X-axis label",
            def: "Percent of studies",
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
            name: "plot_width",
            label: "Plot width (px)",
            def: 400,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "row_height",
            label: "Row height (px)",
            def: 30,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_top",
            label: "Plot padding-top (px)",
            def: 40,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_right",
            label: "Plot padding-right (px)",
            def: 25,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_bottom",
            label: "Plot padding-bottom (px)",
            def: 40,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_left",
            label: "Plot padding-left (px)",
            def: 70,
            tab: "overall",
        },
        {
            type: CheckboxField,
            name: "show_values",
            label: "Show values on plot",
            def: true,
            tab: "overall",
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
            type: IntegerField,
            name: "legend_x",
            label: "Legend x-location (px)",
            def: -1,
            helpText:
                "Set to -1 to be at the left, or 9999 to be at the right (or any value inbetween)",
            tab: "legend",
        },
        {
            type: IntegerField,
            name: "legend_y",
            label: "Legend y-location (px)",
            def: 9999,
            helpText:
                "Set to -1 to be at the top, or 9999 to be at the bottom (or any value inbetween)",
            tab: "legend",
        },
    ],
});

export default RoBBarchartForm;
