import Endpoint from "animal/Endpoint";
import _ from "lodash";
import {renderClientSideAutosuggest} from "shared/components/Autocomplete";
import Crossview from "summary/summary/Crossview";
import CrossviewPlot from "summary/summary/CrossviewPlot";

import $ from "$";

import {DATA_FILTER_OPTIONS, filterLogicHelpText, filterQueryHelpText} from "../summary/filters";
import BaseVisualForm from "./BaseVisualForm";
import {CheckboxField, ColorField, IntegerField, RadioField, TextField} from "./Fields";
import {
    ReferenceLabelField,
    ReferenceLineField,
    ReferenceRangeField,
    TableField,
} from "./TableFields";

class CrossviewSelectorField extends TableField {
    renderHeader() {
        return $("<tr>")
            .append(
                "<th>Field name</th>",
                "<th>Header name</th>",
                "<th>Values</th>",
                "<th>Number of columns</th>",
                "<th>X position</th>",
                "<th>Y position</th>",
                this.thOrdering({showNew: true})
            )
            .appendTo(this.$thead);
    }

    addRow() {
        var self = this,
            nameTd = this.addTdSelect("name", _.keys(CrossviewPlot._filters)).attr(
                "class",
                "valuesSome"
            ),
            valuesTd = this.addTdSelectMultiple("values", []),
            values = valuesTd.find("select").attr("size", 8).css("overflow-y", "scroll"),
            name = nameTd.find("select"),
            setValues = function (fld) {
                var isLog = $('input[name="dose_isLog"]').prop("checked"),
                    opts = _.chain(CrossviewPlot.get_options(self.parent.endpoints, fld, isLog))
                        .map(d => `<option value="${d}" selected>${d}</option>`)
                        .value();
                values.html(opts);
            },
            allValues,
            headerNameTd = this.addTdText("headerName", ""),
            setDefaultHeaderName = function (val) {
                headerNameTd.find("input").val(CrossviewPlot._filters[val]);
            };

        allValues = $('<input class="form-check-input" name="allValues" type="checkbox" checked>')
            .on("change", function () {
                if ($(this).prop("checked")) {
                    values.hide();
                } else {
                    values.show();
                    setValues(name.val());
                }
            })
            .trigger("change");

        $('<div class="form-check">')
            .append(allValues)
            .append('<label class="form-check-label" for="defaultCheck1">Use all values</label>')
            .prependTo(valuesTd);

        name.on("change", function () {
            var val = $(this).val();
            setValues(val);
            setDefaultHeaderName(val);
        }).trigger("change");

        return $("<tr>")
            .append(
                nameTd,
                headerNameTd,
                valuesTd,
                this.addTdInt("columns", 1),
                this.addTdInt("x", 0),
                this.addTdInt("y", 0),
                this.tdOrdering()
            )
            .appendTo(this.$tbody);
    }

    fromSerializedRow(d, i) {
        var row = this.addRow();
        row.find('select[name="name"]').val(d.name);
        row.find('input[name="headerName"]').val(d.headerName);
        row.find('input[name="allValues"]').prop("checked", d.allValues).trigger("change");
        row.find('select[name="values"]').val(d.values);
        row.find('input[name="columns"]').val(d.columns);
        row.find('input[name="x"]').val(d.x);
        row.find('input[name="y"]').val(d.y);
    }

    toSerializedRow(row) {
        row = $(row);
        return {
            name: row.find('select[name="name"]').val(),
            headerName: row.find('input[name="headerName"]').val(),
            allValues: row.find('input[name="allValues"]').prop("checked"),
            values: row.find('select[name="values"]').val(),
            columns: parseInt(row.find('input[name="columns"]').val(), 10),
            x: parseInt(row.find('input[name="x"]').val(), 10),
            y: parseInt(row.find('input[name="y"]').val(), 10),
        };
    }
}

class CrossviewColorFilterField extends TableField {
    renderHeader() {
        return $("<tr>")
            .append(
                "<th>Field name</th>",
                "<th>Field value</th>",
                "<th>Legend name</th>",
                "<th>Color</th>",
                this.thOrdering({showNew: true})
            )
            .appendTo(this.$thead);
    }

    addRow() {
        var self = this,
            fieldTd = this.addTdSelect("field", _.keys(CrossviewPlot._filters)).attr(
                "class",
                "valuesSome"
            ),
            valueTd = this.addTdSelect("value", []),
            headerNameTd = this.addTdText("headerName"),
            headerName = headerNameTd.find("input"),
            field = fieldTd.find("select"),
            value = valueTd.find("select"),
            setValues = function () {
                var isLog = $('input[name="dose_isLog"]').prop("checked"),
                    opts = _.chain(
                        CrossviewPlot.get_options(self.parent.endpoints, field.val(), isLog)
                    )
                        .map(d => `<option value="${d}" selected>${d}</option>`)
                        .value();
                value.html(opts);
            },
            setDefaultHeaderName = function (val) {
                headerName.val(value.val());
            };

        field
            .on("change", function () {
                setValues();
                setDefaultHeaderName();
            })
            .trigger("change");
        value.on("change", setDefaultHeaderName).trigger("change");

        return $("<tr>")
            .append(
                fieldTd,
                valueTd,
                headerNameTd,
                this.addTdColor("color", "#8BA870"),
                this.tdOrdering()
            )
            .appendTo(this.$tbody);
    }

    fromSerializedRow(d, i) {
        var row = this.addRow();
        row.find('select[name="field"]').val(d.field).trigger("change");
        row.find('select[name="value"]').val(d.value);
        row.find('input[name="headerName"]').val(d.headerName);
        row.find('input[name="color"]').val(d.color);
    }

    toSerializedRow(row) {
        row = $(row);
        return {
            field: row.find('select[name="field"]').val(),
            value: row.find('select[name="value"]').val(),
            headerName: row.find('input[name="headerName"]').val(),
            color: row.find('input[name="color"]').val(),
        };
    }
}

class CrossviewEndpointFilterField extends TableField {
    renderHeader() {
        return $("<tr>")
            .append(
                "<th>Field name</th>",
                "<th>Filter type</th>",
                "<th>Value</th>",
                this.thOrdering({showNew: true})
            )
            .appendTo(this.$thead);
    }

    addRow() {
        var fieldTd = this.addTdSelect("field", _.keys(CrossviewPlot._filters)),
            field = fieldTd.find("select"),
            valueTd = this.addTdText("value"),
            setAutocomplete = () => {
                var isLog = $('input[name="dose_isLog"]').prop("checked"),
                    options = CrossviewPlot.get_options(this.parent.endpoints, field.val(), isLog);
                renderClientSideAutosuggest(valueTd[0], "value", "", options);
            };

        field.on("change", setAutocomplete).trigger("change");

        return $("<tr>")
            .append(
                fieldTd,
                this.addTdSelectLabels("filterType", DATA_FILTER_OPTIONS),
                valueTd,
                this.tdOrdering()
            )
            .appendTo(this.$tbody);
    }

    fromSerializedRow(d, i) {
        var row = this.addRow();
        row.find('select[name="field"]').val(d.field).trigger("change");
        row.find('select[name="filterType"]').val(d.filterType);
        row.find('input[name="value"]').val(d.value);
    }

    toSerializedRow(row) {
        row = $(row);
        return {
            field: row.find('select[name="field"]').val(),
            filterType: row.find('select[name="filterType"]').val(),
            value: row.find('input[name="value"]').val(),
        };
    }
}

class CrossviewForm extends BaseVisualForm {
    buildPreview($parent, data) {
        this.preview = new Crossview(data).displayAsPage($parent.empty(), {
            dev: true,
        });
    }

    updateSettingsFromPreview() {
        var plotSettings = JSON.stringify(this.preview.data.settings);
        $("#id_settings").val(plotSettings);
        this.unpackSettings();
    }

    afterGetDataHook(data) {
        this.endpoints = data.endpoints.map(function (d) {
            var e = new Endpoint(d);
            e.doseUnits.activate(data.dose_units);
            return e;
        });
    }

    initDataForm() {
        var fields = [
            ["system", "systems"],
            ["organ", "organs"],
            ["effect", "effects"],
            ["effect_subtype", "effect_subtypes"],
            ["study", "studies"],
            ["effect_tag", "effect_tags"],
        ];

        _.each(fields, function (d) {
            $(`#id_prefilter_${d[0]}`)
                .on("change", function () {
                    var div = $(`#div_id_${d[1]}`);
                    $(this).prop("checked") ? div.show(1000) : div.hide(0);
                })
                .trigger("change");
        });
    }
}

_.extend(CrossviewForm, {
    tabs: [
        {name: "overall", label: "General settings"},
        {name: "filters", label: "Crossview filters"},
        {name: "references", label: "References"},
        {name: "styles", label: "Styles"},
        {name: "endpointFilters", label: "Endpoint filters"},
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
            def: "Dose (<add units>)",
            tab: "overall",
        },
        {
            type: TextField,
            name: "yAxisLabel",
            label: "Y-axis label",
            def: "% change from control (continuous), % incidence (dichotomous)",
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "width",
            label: "Overall width (px)",
            def: 1100,
            helpText: "Overall width, including plot and tags",
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "height",
            label: "Overall height (px)",
            def: 600,
            helpText: "Overall height, including plot and tags",
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "inner_width",
            label: "Plot width (px)",
            def: 940,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "inner_height",
            label: "Plot height (px)",
            def: 520,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_left",
            label: "Plot padding-left (px)",
            def: 75,
            tab: "overall",
        },
        {
            type: IntegerField,
            name: "padding_top",
            label: "Plot padding-top (px)",
            def: 45,
            tab: "overall",
        },
        {
            type: CheckboxField,
            name: "dose_isLog",
            label: "Use logscale for dose",
            def: true,
            tab: "overall",
        },
        {
            type: TextField,
            name: "dose_range",
            label: "Dose-axis range",
            tab: "overall",
            helpText: 'If left blank, calculated automatically from data (ex: "1, 100").',
        },
        {
            type: TextField,
            name: "response_range",
            label: "Response-axis range",
            tab: "overall",
            helpText: 'If left blank, calculated automatically from data (ex: "-0.5, 2.5").',
        },
        {
            type: IntegerField,
            name: "title_x",
            label: "Title x-offset (px)",
            def: 0,
            tab: "overall",
            helpText: "x-offset from default title location (centered at top of plot)",
        },
        {
            type: IntegerField,
            name: "title_y",
            label: "Title y-offset (px)",
            def: 0,
            tab: "overall",
            helpText: "y-offset from default title location (centered at top of plot)",
        },
        {
            type: IntegerField,
            name: "xlabel_x",
            label: "X label x-offset (px)",
            def: 0,
            tab: "overall",
            helpText: "x-offset from default location (centered below x-axis)",
        },
        {
            type: IntegerField,
            name: "xlabel_y",
            label: "X label y-offset (px)",
            def: 0,
            tab: "overall",
            helpText: "y-offset from default location (centered below x-axis)",
        },
        {
            type: IntegerField,
            name: "ylabel_x",
            label: "Y label x-offset (px)",
            def: 0,
            tab: "overall",
            helpText: "x-offset from default location (centered left of y-axis)",
        },
        {
            type: IntegerField,
            name: "ylabel_y",
            label: "Y label y-offset (px)",
            def: 0,
            tab: "overall",
            helpText: "y-offset from default location (centered left of y-axis)",
        },
        {
            type: CrossviewSelectorField,
            helpText:
                "Crossview filters are displayed as text on the chart, which is highlighted when a relevant endpoint is selected.",
            prependSpacer: false,
            name: "filters",
            colWidths: [15, 20, 20, 10, 10, 10, 15],
            addBlankRowIfNone: true,
            tab: "filters",
        },
        {
            type: ReferenceLineField,
            prependSpacer: false,
            label: "Dose reference line",
            name: "reflines_dose",
            colWidths: [20, 40, 20, 20],
            addBlankRowIfNone: true,
            tab: "references",
        },
        {
            type: ReferenceRangeField,
            prependSpacer: true,
            label: "Dose reference range",
            name: "refranges_dose",
            colWidths: [10, 10, 40, 20, 20],
            addBlankRowIfNone: true,
            tab: "references",
        },
        {
            type: ReferenceLineField,
            prependSpacer: true,
            label: "Response reference line",
            name: "reflines_response",
            colWidths: [20, 40, 20, 20],
            addBlankRowIfNone: true,
            tab: "references",
        },
        {
            type: ReferenceRangeField,
            prependSpacer: true,
            label: "Response reference range",
            name: "refranges_response",
            colWidths: [10, 10, 40, 20, 20],
            addBlankRowIfNone: true,
            tab: "references",
        },
        {
            type: ReferenceLabelField,
            prependSpacer: true,
            label: "Figure captions",
            name: "labels",
            colWidths: [45, 15, 10, 10, 10, 10],
            addBlankRowIfNone: true,
            tab: "references",
        },
        {
            type: ColorField,
            name: "colorBase",
            label: "Base path color",
            tab: "styles",
            helpText: "Must be valid CSS color name",
            def: "#cccccc",
        },
        {
            type: ColorField,
            name: "colorHover",
            label: "Hover path color",
            tab: "styles",
            helpText: "Must be valid CSS color name",
            def: "#ff4040",
        },
        {
            type: ColorField,
            name: "colorSelected",
            label: "Selected path color",
            tab: "styles",
            helpText: "Must be valid CSS color name",
            def: "#6495ed",
        },
        {
            type: CrossviewColorFilterField,
            prependSpacer: true,
            label: "Color filters",
            name: "colorFilters",
            colWidths: [23, 23, 22, 22, 10],
            addBlankRowIfNone: false,
            tab: "styles",
            helpText:
                "Custom colors can be applied to paths; these colors are applied based on selectors added below. The first-row is applied last; so if two rules match the same path, the upper-row color will be applied.",
        },
        {
            type: CheckboxField,
            name: "colorFilterLegend",
            label: "Show color filter legend",
            def: true,
            tab: "styles",
        },
        {
            type: TextField,
            name: "colorFilterLegendLabel",
            label: "Color filter legend title",
            def: "Color filters",
            tab: "styles",
        },
        {
            type: IntegerField,
            name: "colorFilterLegendX",
            label: "Color filter legend X position",
            def: 0,
            tab: "styles",
        },
        {
            type: IntegerField,
            name: "colorFilterLegendY",
            label: "Color filter legend Y position",
            def: 0,
            tab: "styles",
        },
        {
            type: CrossviewEndpointFilterField,
            helpText:
                "Filters used to determine which dose-response datasets should be included; by default all plottable datasets are included.",
            prependSpacer: false,
            name: "endpointFilters",
            colWidths: [25, 25, 38, 12],
            addBlankRowIfNone: false,
            tab: "endpointFilters",
        },
        {
            type: RadioField,
            label: "Filter logic",
            helpText: filterLogicHelpText,
            name: "endpointFilterLogic",
            def: "and",
            options: [
                {label: "AND", value: "and"},
                {label: "OR", value: "or"},
                {label: "CUSTOM", value: "custom"},
            ],
            tab: "endpointFilters",
        },
        {
            type: TextField,
            name: "filtersQuery",
            helpText:
                filterQueryHelpText +
                ". In the above table, the first row is 1, second row is 2, etc.",
            def: "",
            tab: "endpointFilters",
        },
    ],
});

export default CrossviewForm;
