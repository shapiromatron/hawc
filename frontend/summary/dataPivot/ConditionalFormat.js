import * as d3 from "d3";
import _ from "lodash";
import HAWCModal from "shared/utils/HAWCModal";

import $ from "$";

import DataPivot from "./DataPivot";
import DataPivotVisualization from "./DataPivotVisualization";
import {buildStyleMap, NULL_CASE} from "./shared";

class _DataPivot_settings_conditionalFormat {
    constructor(parent, data, settings) {
        this.parent = parent;
        this.data = data;
        this.settings = settings;
        this.status = $("<div>");

        this._status_text = $('<span style="padding-right: 10px">').appendTo(this.status);

        this.modal = new HAWCModal();
        this._showModal = $('<button class="btn btn-sm btn-info" type="button">')
            .on("click", this._show_modal.bind(this))
            .appendTo(this.status);

        this._update_status();
    }

    _update_status() {
        var status = this.data.length > 0 ? "Enabled" : "None",
            modal = this.data.length > 0 ? "Edit" : "Create";

        this._status_text.text(status);
        this._showModal.text(modal);
    }

    _show_modal() {
        var header = $("<h4>").html(`Conditional formatting: <i>${this.parent.getName()}<i>`),
            footer = this._getFooter();

        this.setModalContent();
        this.modal
            .addHeader(header)
            .addFooter(footer, {noClose: true})
            .show({maxWidth: 1200});
    }

    close_modal(save) {
        if (save) {
            this._save_conditions();
        }
        this._update_status();
        this.modal.hide();
    }

    setModalContent() {
        var body = this.modal.getBody();
        body.empty();

        // add placeholder if no conditions are set
        this.blank = $("<span>").appendTo(body);
        this._set_empty_message();

        // draw conditions
        this.conditionals = [];
        this.data.forEach(v => {
            this.conditionals.push(new _DataPivot_settings_conditional(body, this, v));
        });
    }

    _getFooter() {
        let add = $('<button type="button" class="btn btn-primary float-left">')
                .text("Add")
                .on("click", this._add_condition.bind(this, null)),
            save = $('<button type="button" class="btn btn-success mx-2 float-left">')
                .text("Save and close")
                .on("click", this.close_modal.bind(this, true)),
            close = $('<button type="button" class="btn btn-light">')
                .text("Close")
                .on("click", this.close_modal.bind(this, false)),
            footer = $("<div>").append(add, save, close);

        return footer;
    }

    _save_conditions() {
        this.data = this.conditionals.map(v => v.get_values());
        this.parent.data_push();
    }

    _set_empty_message() {
        if (this.data.length === 0) {
            this.blank.text("No conditions have been set.");
        } else {
            this.blank.empty();
        }
    }

    _add_condition(values) {
        var body = this.modal.getBody();
        this._set_empty_message();
        this.conditionals.push(new _DataPivot_settings_conditional(body, this, values));
    }

    delete_condition(conditional) {
        _.remove(this.conditionals, d => d === conditional);
        this._set_empty_message();
    }

    getConditionTypes() {
        switch (this.settings.type) {
            case "symbols":
                return ["point-size", "point-color", "discrete-style"];

            case "lines":
                return ["discrete-style"];

            case "rectangles":
                return ["discrete-style"];

            default:
                return [];
        }
    }
}
_.extend(_DataPivot_settings_conditionalFormat, {
    defaults: {
        field_name: NULL_CASE,
        condition_type: "point-size",
        min_size: 50,
        max_size: 150,
        min_color: "#EEE13D",
        max_color: "#2320D9",
        discrete_styles: [],
    },
});

class _DataPivot_ColorGradientSVG {
    constructor(svg, start_color, stop_color) {
        svg = d3.select(svg);
        var gradient = svg
            .append("svg:defs")
            .append("svg:linearGradient")
            .attr("id", "gradient")
            .attr("x1", "0%")
            .attr("y1", "100%")
            .attr("x2", "100%")
            .attr("y2", "100%")
            .attr("spreadMethod", "pad");

        this.start = gradient
            .append("svg:stop")
            .attr("offset", "0%")
            .attr("stop-color", start_color)
            .attr("stop-opacity", 1);

        this.stop = gradient
            .append("svg:stop")
            .attr("offset", "100%")
            .attr("stop-color", stop_color)
            .attr("stop-opacity", 1);

        svg.append("svg:rect")
            .attr("width", "100%")
            .attr("height", "100%")
            .style("fill", "url(#gradient)");
    }

    update_start_color(color) {
        this.start.attr("stop-color", color);
    }

    update_stop_color(color) {
        this.stop.attr("stop-color", color);
    }
}

class _DataPivot_settings_conditional {
    constructor(el, parent, values) {
        this.inputs = [];

        values = values || {};
        if (values.discrete_styles === undefined) {
            values.discrete_styles = [];
        }

        var self = this,
            dp = parent.parent.data_pivot,
            formattingTypes = parent.getConditionTypes(),
            defaults = _DataPivot_settings_conditionalFormat.defaults,
            div = $('<div class="well">').appendTo(el),
            add_input_row = function(parent, desc_txt, inp) {
                var lbl = $("<label>").html(desc_txt);
                parent.append(lbl, inp);
            },
            fieldName = dp.column_select_manager
                .createSelect(true, {name: "field_name"})
                .val(values.field_name || defaults.field_name),
            conditionType = $('<select class="form-control" name="condition_type">')
                .html(formattingTypes.map(v => `<option value="${v}">${v}</option>`))
                .val(values.condition_type || defaults.condition_type),
            changeConditionType = function() {
                div.find(".conditionalDivs").hide();
                div.find(`.${conditionType.val()}`).fadeIn();
            };

        // add delete button
        $('<button type="button" class="close">')
            .text("x")
            .on("click", function() {
                div.remove();
                parent.delete_condition(self);
            })
            .prependTo(div);

        // add master conditional inputs and divs for changing fields
        add_input_row(div, "Condition field", fieldName);
        add_input_row(div, "Condition type", conditionType);
        div.append("<hr>");
        formattingTypes.forEach(function(v) {
            $(`<div class="conditionalDivs ${v}">`)
                .appendTo(div)
                .hide();
        });

        // build min/max for size and color
        var min_size = $(
                '<input class="form-control" name="min_size" type="range" min="0" max="500" step="5">'
            ).val(values.min_size || defaults.min_size),
            max_size = $(
                '<input class="form-control" name="max_size" type="range" min="0" max="500" step="5">'
            ).val(values.max_size || defaults.max_size),
            min_color = $('<input class="form-control" name="min_color" type="color">').val(
                values.min_color || defaults.min_color
            ),
            max_color = $('<input class="form-control" name="max_color" type="color">').val(
                values.max_color || defaults.max_color
            ),
            svg = $(
                '<svg role="image" aria-label="Color gradient" width="150" height="25" class="d3" style="margin-top: 10px"></svg>'
            ),
            gradient = new _DataPivot_ColorGradientSVG(svg[0], min_color.val(), max_color.val());

        // add event-handlers to change gradient color
        min_color.change(function(v) {
            gradient.update_start_color(min_color.val());
        });
        max_color.change(function(v) {
            gradient.update_stop_color(max_color.val());
        });

        // add size values to size div
        var ps = div.find(".point-size"),
            min_max_ps = $("<p>").appendTo(ps);
        add_input_row(ps, "Minimum point-size", DataPivot.rangeInputDiv(min_size));
        add_input_row(ps, "Maximum point-size", DataPivot.rangeInputDiv(max_size));

        // add color values to color div
        var pc = div.find(".point-color"),
            min_max_pc = $("<p>").appendTo(pc);
        add_input_row(pc, "Minimum color", min_color);
        add_input_row(pc, "Maximum color", max_color);
        pc.append("<br>", svg);

        this.inputs.push(fieldName, conditionType, min_size, max_size, min_color, max_color);

        // get unique values and set values
        var buildStyleSelectors = function() {
            // show appropriate div
            var discrete = div.find(".discrete-style");
            self.discrete_styles = [];
            discrete.empty();

            var subset = DataPivotVisualization.filter(
                    dp.data,
                    dp.settings.filters,
                    dp.settings.plot_settings.filter_logic,
                    dp.settings.plot_settings.filter_query
                ),
                arr = subset.map(v => v[fieldName.val()]),
                vals = DataPivot.getRowDetails(arr);

            if (conditionType.val() === "discrete-style") {
                // exit early if there are no tokens
                if (vals.unique_tokens.length === 0) {
                    discrete.append(
                        "<p><i>The selected condition field contains no non-null values. Please select another field.</i></p>"
                    );
                    return;
                }

                // build rows for all unique items; tokens must be a string
                let mapping = buildStyleMap(values, true);
                vals.unique_tokens.forEach(v => {
                    var select = dp.style_manager
                        .add_select(parent.settings.type, mapping.get(v) || NULL_CASE, true)
                        .data("key", v);
                    self.discrete_styles.push(select);
                    add_input_row(discrete, `Style for <kbd>${v}</kbd>:`, select);
                });
            } else {
                var txt = `Selected items in <i>${fieldName.val()}</i> `;
                if (vals.range) {
                    txt += `contain values ranging from ${vals.range[0]} to ${vals.range[1]}.`;
                } else {
                    txt += "have no range of values, please select another column.";
                }

                min_max_pc.html(txt);
                min_max_ps.html(txt);
            }
        };

        // add event-handlers and fire to initialize
        fieldName.on("change", buildStyleSelectors);
        conditionType.on("change", function() {
            buildStyleSelectors();
            changeConditionType();
        });

        changeConditionType();
        buildStyleSelectors();
    }

    get_values() {
        var values = {discrete_styles: []};
        this.inputs.forEach(function(v) {
            values[v.attr("name")] = parseInt(v.val(), 10) || v.val();
        });
        this.discrete_styles.forEach(function(v) {
            values.discrete_styles.push({key: v.data("key"), style: v.val()});
        });
        return values;
    }
}

export {_DataPivot_settings_conditionalFormat};
export {_DataPivot_ColorGradientSVG};
export {_DataPivot_settings_conditional};
