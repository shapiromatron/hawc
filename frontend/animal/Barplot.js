import $ from "$";
import _ from "lodash";
import * as d3 from "d3";

import D3Plot from "utils/D3Plot";

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
        this.build_plot_skeleton(true);
        this.add_title();
        this.add_axes();
        this.add_bars();
        this.add_error_bars();
        this.build_x_label();
        this.build_y_label();
        this.add_final_rectangle();
        this.add_legend();
        this.customize_menu();

        var plot = this;
        this.y_axis_label.on("click", function(v) {
            plot.toggle_y_axis();
        });
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
        var plot = this;
        var options = {
            id: "toggle_y_axis",
            cls: "btn btn-mini",
            title: "Change y-axis scale (shortcut: click the y-axis label)",
            text: "",
            icon: "icon-resize-vertical",
            on_click() {
                plot.toggle_y_axis();
            },
        };
        plot.add_menu_button(options);

        if (this.endpoint.doses.length > 1) {
            options = {
                id: "toggle_dose_units",
                cls: "btn btn-mini",
                title: "Change dose-units representation",
                text: "",
                icon: "icon-certificate",
                on_click() {
                    plot.endpoint.toggle_dose_units();
                },
            };
            plot.add_menu_button(options);
        }
    }

    toggle_y_axis() {
        if (this.endpoint.data.data_type == "C") {
            if (this.y_axis_settings.scale_type == "linear") {
                this.y_axis_settings.scale_type = "log";
                this.y_axis_settings.number_ticks = 1;
                var formatNumber = d3.format(",");
                this.y_axis_settings.label_format = formatNumber;
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
        this.buff = 0.05; // addition numerical-spacing around dose/response units

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
        var values,
            val,
            txt,
            cls,
            sigs_data,
            e = this.endpoint,
            data_type = e.data.data_type,
            min = Infinity,
            max = -Infinity;

        values = _.chain(this.endpoint.data.groups)
            .map(function(v, i) {
                if (data_type == "C") {
                    val = v.response;
                    txt = v.response;
                } else if (data_type == "P") {
                    val = v.response;
                    txt = e.get_pd_string(v);
                } else {
                    val = v.incidence / v.n;
                    txt = val;
                }

                cls = "dose_bars";
                if (e.data.NOEL == i) cls += " NOEL";
                if (e.data.LOEL == i) cls += " LOEL";

                min = Math.min(min, v.lower_ci || val);
                max = Math.max(max, v.upper_ci || val);

                return {
                    isReported: v.isReported,
                    dose: v.dose,
                    value: val,
                    high: v.upper_ci,
                    low: v.lower_ci,
                    txt,
                    classes: cls,
                    significance_level: v.significance_level,
                };
            })
            .filter(function(d) {
                return d.isReported;
            })
            .value();

        sigs_data = _.chain(values)
            .filter(function(v) {
                return v.significance_level > 0;
            })
            .map(function(v) {
                return {
                    x: v.dose,
                    y: v.high || v.value,
                    significance_level: v.significance_level,
                };
            })
            .value();

        if (this.endpoint.data.data_type == "C") {
            min = min - max * this.buff;
        } else {
            min = 0;
        }
        max = max * (1 + this.buff);
        if (this.default_y_scale == "log") {
            min = Math.pow(10, Math.floor(Math.log10(min)));
            max = Math.pow(10, Math.ceil(Math.log10(max)));
        }

        _.extend(this, {
            title_str: this.endpoint.data.name,
            x_label_text: `Doses (${this.endpoint.dose_units})`,
            y_label_text: `Response (${this.endpoint.data.response_units})`,
            values,
            sigs_data,
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

        this.bars.append("svg:title").text(d => d.txt);

        var sigs_group = this.vis.append("g");
        this.sigs = sigs_group
            .selectAll("text")
            .data(this.sigs_data)
            .enter()
            .append("svg:text")
            .attr("x", d => x(d.x) + x.bandwidth() / 2)
            .attr("y", d => y(d.y))
            .attr("text-anchor", "middle")
            .style("font-size", "18px")
            .style("font-weight", "bold")
            .style("cursor", "pointer")
            .text("*");

        this.sigs_labels = this.sigs.append("svg:title").text(function(d) {
            return `Statistically significant at ${d.significance_level}`;
        });
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

        //rebuild y-axis
        this.yAxis
            .scale(y)
            .ticks(this.y_axis_settings.number_ticks, this.y_axis_settings.label_format);

        this.vis
            .selectAll(".y_axis")
            .transition()
            .duration(1000)
            .call(this.yAxis);

        this.rebuild_y_gridlines({animate: true});

        //rebuild error-bars
        var opt = {
            y1(d) {
                return y(d.low);
            },
            y2(d) {
                return y(d.high);
            },
        };
        this.build_line(opt, this.error_bars_vertical);

        opt.y2 = function(d) {
            return y(d.low);
        };
        this.build_line(opt, this.error_bars_lower);

        opt = {
            y1(d) {
                return y(d.high);
            },
            y2(d) {
                return y(d.high);
            },
        };
        this.build_line(opt, this.error_bars_upper);

        //rebuild dose-bars
        this.bars
            .transition()
            .duration(1000)
            .attr("y", d => y(d.value))
            .attr("height", d => min - y(d.value));

        this.sigs
            .transition()
            .duration(1000)
            .attr("y", d => y(d.y));
    }

    add_error_bars() {
        var hline_width = this.w * 0.02,
            x = this.x_scale,
            y = this.y_scale,
            bars = this.values.filter(function(v) {
                return $.isNumeric(v.low) && $.isNumeric(v.high);
            });

        this.error_bar_group = this.vis.append("g").attr("class", "error_bars");

        var bar_options = {
            data: bars,
            x1(d) {
                return x(d.dose) + x.bandwidth() / 2;
            },
            y1(d) {
                return y(d.low);
            },
            x2(d) {
                return x(d.dose) + x.bandwidth() / 2;
            },
            y2(d) {
                return y(d.high);
            },
            classes: "dr_err_bars",
            append_to: this.error_bar_group,
        };
        this.error_bars_vertical = this.build_line(bar_options);

        $.extend(bar_options, {
            x1(d, i) {
                return x(d.dose) + x.bandwidth() / 2 - hline_width;
            },
            y1(d) {
                return y(d.low);
            },
            x2(d, i) {
                return x(d.dose) + x.bandwidth() / 2 + hline_width;
            },
            y2(d) {
                return y(d.low);
            },
        });
        this.error_bars_lower = this.build_line(bar_options);

        $.extend(bar_options, {
            y1(d) {
                return y(d.high);
            },
            y2(d) {
                return y(d.high);
            },
        });
        this.error_bars_upper = this.build_line(bar_options);
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
        legend_settings.box_w = 110;
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
