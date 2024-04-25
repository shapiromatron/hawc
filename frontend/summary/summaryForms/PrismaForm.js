import _ from "lodash";

import $ from "$";

import BaseVisualForm from "./BaseVisualForm";


class PrismaForm extends BaseVisualForm {
    afterGetDataHook(data) {
        // Prisma.transformData(data);
    }

    buildPreview($parent, data) {
        // this.preview = new Prisma(data).displayAsPage($parent.empty(), { dev: true });
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

_.extend(PrismaForm, {
    tabs: [
        { name: "overall", label: "General settings" },
        { name: "metrics", label: "Included metrics" },
        { name: "excluded_scores", label: "Included judgments" },
        { name: "legend", label: "Legend settings" },
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
            def: 330,
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

export default PrismaForm;
