import * as d3 from "d3";
import _ from "lodash";
import D3Plot from "shared/utils/D3Plot";
import h from "shared/utils/helpers";

import $ from "$";

class Barplot extends D3Plot {
    constructor(endpoint, plot_id, options, parent) {
        super(...arguments);
        this.parent = parent;
        this.endpoint = endpoint;
        this.plot_div = $(plot_id);
        this.options = options || {build_plot_startup: true};
        this.set_defaults();
        this.get_dataset_info();
        this.endpoint.addObserver(this);
        if (this.options.build_plot_startup) {
            this.build_plot();
        }
    }

    build_plot() {
        this.plot_div.html("");
        this.get_plot_sizes();
        this.build_plot_skeleton(true, "A barchart of response with confidence intervals");
        this.add_title(null, null, {wrapWidth: 325});
        this.add_axes();
        this.add_bars();
        this.add_error_bars();
        this.build_x_label();
        this.build_y_label();
        this.add_final_rectangle();
        this.add_legend();
        this.customize_menu();
        this.trigger_resize();
    }

    customize_menu() {
        if (this.menu_div) {
            this.menu_div.remove();
            delete this.menu_div;
        }
        this.add_menu();
        if (this.parent) {
            this.parent.add_toggle_button(this);
        }
        this.add_menu_button({
            id: "toggle_y_axis",
            cls: "btn btn-sm",
            title: "Change y-axis scale",
            text: "",
            icon: "fa fa-arrows-v",
            on_click: () => this.toggle_y_axis(),
        });

        if (this.endpoint.doseUnits.numUnits() > 1) {
            this.add_menu_button({
                id: "nextDoseUnits",
                cls: "btn btn-sm",
                title: "Change dose-units representation",
                text: "",
                icon: "fa fa-certificate",
                on_click: () => this.endpoint.doseUnits.next(),
            });
        }
    }

    toggle_y_axis() {
        if (this.endpoint.data.data_type == "C") {
            if (this.y_axis_settings.scale_type == "linear") {
                this.y_axis_settings.scale_type = "log";
                this.y_axis_settings.number_ticks = h.numLogTicks(this.y_axis_settings.domain);
                this.y_axis_settings.label_format = h.numericAxisFormat;
            } else {
                this.y_axis_settings.scale_type = "linear";
                this.y_axis_settings.number_ticks = 10;
                this.y_axis_settings.label_format = undefined;
            }
        } else {
            var d = this.y_axis_settings.domain;
            if (d[0] === 0 && d[1] === 1) {
                this.y_axis_settings.domain = [this.min_y, this.max_y];
            } else {
                this.y_axis_settings.domain = [0, 1];
            }
        }
        this.y_scale = this._build_scale(this.y_axis_settings);
        this.y_axis_change_chart_update();
    }

    update(status) {
        if (status.status === "dose_changed") {
            this.dose_scale_change();
        }
    }

    dose_scale_change() {
        this.get_dataset_info();
        if (this.parent && this.parent.plot === this) {
            this.x_axis_settings.domain = _.map(this.values, "dose");
            this.x_scale = this._build_scale(this.x_axis_settings);
            this.x_axis_change_chart_update();
            this.build_x_label();
        }
    }

    set_defaults() {
        // Default settings
        this.padding = {top: 40, right: 20, bottom: 40, left: 60};

        this.x_axis_settings = {
            scale_type: "ordinal",
            text_orient: "bottom",
            axis_class: "axis x_axis",
            gridlines: true,
            gridline_class: "primary_gridlines x_gridlines",
            axis_labels: true,
            label_format: undefined, //default
        };

        this.y_axis_settings = {
            scale_type: this.options.default_y_axis || "linear",
            text_orient: "left",
            axis_class: "axis y_axis",
            gridlines: true,
            gridline_class: "primary_gridlines y_gridlines",
            number_ticks: 10,
            axis_labels: true,
            label_format: undefined, //default
        };
    }

    get_plot_sizes() {
        this.w = this.plot_div.width() - this.padding.left - this.padding.right; // plot width
        this.h = this.w; //plot height
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + "px",
        });
    }

    get_dataset_info() {
        this.get_plot_sizes();
        // space lines in half-increments
        let e = this.endpoint,
            isDichotomous = e.isDichotomous(),
            data_type = e.data.data_type,
            min = Infinity,
            max = -Infinity,
            values = _.chain(this.endpoint.data.groups)
                .filter(d => d.isReported)
                .map((v, i) => {
                    let val, label, cls;

                    if (["C", "P"].includes(data_type)) {
                        val = v.response;
                        label = "";
                    } else if (this.endpoint.isDichotomous()) {
                        val = v.incidence / v.n;
                        label = "";
                    } else {
                        console.error("Unknown data_type");
                    }

                    cls = "dose_bars";
                    if (e.data.NOEL == i) cls += " NOEL";
                    if (e.data.LOEL == i) cls += " LOEL";

                    min = Math.min(min, v.lower_ci || val);
                    max = Math.max(max, v.upper_ci || val);

                    const is_significant = _.isNumber(v.significance_level);
                    if (is_significant) {
                        label += " *";
                    }
                    return {
                        dose: v.dose,
                        value: val,
                        high: v.upper_ci,
                        low: v.lower_ci,
                        classes: cls,
                        significance_level: v.significance_level,
                        is_significant,
                        label,
                        label_y: isDichotomous ? val : val | v.upper_ci,
                    };
                })
                .value();

        min = isDichotomous ? 0 : min;
        _.extend(this, {
            title_str: this.endpoint.data.name,
            x_label_text: `Doses (${this.endpoint.doseUnits.activeUnit.name})`,
            y_label_text: `Response (${this.endpoint.data.response_units})`,
            values,
            min_y: min,
            max_y: max,
        });
    }

    add_axes() {
        $.extend(this.x_axis_settings, {
            domain: _.map(this.values, "dose"),
            number_ticks: this.values.length,
            rangeRound: [0, this.w],
            x_translate: 0,
            y_translate: this.h,
        });

        $.extend(this.y_axis_settings, {
            domain: [this.min_y, this.max_y],
            rangeRound: [this.h, 0],
            label_format: this.endpoint.isDichotomous() ? d3.format(".0%") : undefined,
            x_translate: 0,
            y_translate: 0,
        });

        this.build_x_axis();
        this.build_y_axis();
    }

    add_bars() {
        var x = this.x_scale,
            y = this.y_scale,
            bar_spacing = 0.1,
            min = y(y.domain()[0]);

        this.dose_bar_group = this.vis.append("g");
        this.bars = this.dose_bar_group
            .selectAll("svg.bars")
            .data(this.values)
            .enter()
            .append("rect")
            .attr("x", d => x(d.dose) + x.bandwidth() * bar_spacing)
            .attr("y", d => y(d.value))
            .attr("width", x.bandwidth() * (1 - 2 * bar_spacing))
            .attr("height", d => min - y(d.value))
            .attr("class", d => d.classes);

        let label_group = this.vis.append("g");
        this.labels = label_group
            .selectAll("text")
            .data(this.values)
            .enter()
            .append("svg:text")
            .attr("x", d => x(d.dose) + x.bandwidth() / 2)
            .attr("y", d => y(d.label_y))
            .attr("text-anchor", "middle")
            .style("font-size", "18px")
            .style("font-weight", "bold")
            .style("cursor", "pointer")
            .text(d => d.label);

        this.labels
            .filter(d => d.is_significant)
            .append("svg:title")
            .text(d => `Statistically significant at ${d.significance_level}`);
    }

    x_axis_change_chart_update() {
        this.xAxis.scale(this.x_scale);
        this.vis
            .selectAll(".x_axis")
            .transition()
            .call(this.xAxis);
    }

    y_axis_change_chart_update() {
        // Assuming the plot has already been constructed once,
        // rebuild plot with updated y-scale.

        var y = this.y_scale,
            min = y(y.domain()[0]);

        // rebuild y-axis
        this.yAxis
            .scale(y)
            .ticks(this.y_axis_settings.number_ticks, this.y_axis_settings.label_format);

        this.vis
            .selectAll(".y_axis")
            .transition()
            .duration(1000)
            .call(this.yAxis);

        this.rebuild_y_gridlines({animate: true});

        // rebuild error-bars
        if (this.error_bar_group) {
            let opts = [
                    {y1: d => y(d.low), y2: d => y(d.high)},
                    {y1: d => y(d.low), y2: d => y(d.low)},
                    {y1: d => y(d.high), y2: d => y(d.high)},
                ],
                doms = [this.error_bars_vertical, this.error_bars_lower, this.error_bars_upper],
                lines_args = _.zip(opts, doms);

            lines_args.forEach(args => this.build_line(args[0], args[1]));
        }

        // rebuild dose-bars
        this.bars
            .transition()
            .duration(1000)
            .attr("y", d => y(d.value))
            .attr("height", d => min - y(d.value));

        this.labels
            .transition()
            .duration(1000)
            .attr("y", d => y(d.label_y));
    }

    add_error_bars() {
        if (this.endpoint.isDichotomous()) {
            return;
        }
        const hline_width = this.w * 0.01,
            x = this.x_scale,
            y = this.y_scale,
            bars = this.values.filter(v => $.isNumeric(v.low) && $.isNumeric(v.high));

        this.error_bar_group = this.vis.append("g").attr("class", "error_bars");
        this.error_bars_vertical = this.build_line({
            data: bars,
            x1: d => x(d.dose) + x.bandwidth() / 2,
            y1: d => y(d.low),
            x2: d => x(d.dose) + x.bandwidth() / 2,
            y2: d => y(d.high),
            classes: "dr_err_bars",
            append_to: this.error_bar_group,
        });
        this.error_bars_lower = this.build_line({
            data: bars,
            x1: d => x(d.dose) + x.bandwidth() / 2 - hline_width,
            y1: d => y(d.low),
            x2: d => x(d.dose) + x.bandwidth() / 2 + hline_width,
            y2: d => y(d.low),
            classes: "dr_err_bars",
            append_to: this.error_bar_group,
        });
        this.error_bars_upper = this.build_line({
            data: bars,
            x1: d => x(d.dose) + x.bandwidth() / 2 - hline_width,
            y1: d => y(d.high),
            x2: d => x(d.dose) + x.bandwidth() / 2 + hline_width,
            y2: d => y(d.high),
            classes: "dr_err_bars",
            append_to: this.error_bar_group,
        });
    }

    add_legend() {
        var legend_settings = {};
        legend_settings.items = [
            {
                text: "Doses",
                classes: "dose_points",
                color: undefined,
            },
        ];
        if (this.plot_div.find(".LOEL").length > 0) {
            legend_settings.items.push({
                text: this.endpoint.data.noel_names.loel,
                classes: "dose_points LOEL",
                color: undefined,
            });
        }
        if (this.plot_div.find(".NOEL").length > 0) {
            legend_settings.items.push({
                text: this.endpoint.data.noel_names.noel,
                classes: "dose_points NOEL",
                color: undefined,
            });
        }
        if (this.plot_div.find(".BMDL").length > 0) {
            legend_settings.items.push({
                text: "BMDL",
                classes: "dose_points BMDL",
                color: undefined,
            });
        }
        legend_settings.item_height = 20;
        legend_settings.box_h = legend_settings.items.length * legend_settings.item_height;
        legend_settings.box_padding = 5;
        legend_settings.dot_r = 5;

        if (this.legend_left) {
            legend_settings.box_l = this.legend_left;
        } else {
            legend_settings.box_l = 10;
        }

        if (this.legend_top) {
            legend_settings.box_t = this.legend_top;
        } else {
            legend_settings.box_t = 10;
        }

        this.build_legend(legend_settings);
    }

    cleanup_before_change() {}
}

export default Barplot;
