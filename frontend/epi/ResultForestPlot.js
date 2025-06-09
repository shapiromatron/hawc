import * as d3 from "d3";
import _ from "lodash";
import D3Plot from "shared/utils/D3Plot";

class ResultForestPlot extends D3Plot {
    constructor(res, $div, options) {
        super();
        this.options = options || this.default_options();
        this.set_defaults();
        this.plot_div = $div;
        this.res = res;
        if (this.options.build_plot_startup) {
            this.build_plot();
        }
    }

    default_options() {
        return {build_plot_startup: true};
    }

    build_plot() {
        this.plot_div.empty();
        this.get_dataset();
        if (!this.isPlottable()) return;
        this.get_plot_sizes();
        this.build_plot_skeleton(true, "A result forestplot");
        this.add_axes();
        this.build_x_label();
        this.draw_visualizations();
        this.add_title();
        this.add_final_rectangle();
        this.add_menu();
        this.resize_plot_dimensions();
        this.trigger_resize();
    }

    get_dataset() {
        var data = this.res.data,
            estimates = _.chain(this.res.resultGroups)
                .filter(function (d) {
                    return d.estimateNumeric();
                })
                .map(function (d) {
                    return {
                        group: d,
                        name: d.data.group.name,
                        estimate: d.data.estimate,
                    };
                })
                .value(),
            lines = _.chain(estimates)
                .map(function (d) {
                    return d.group.getIntervals();
                })
                .filter(function (d) {
                    return _.isNumber(d.lower_bound_interval) && _.isNumber(d.upper_bound_interval);
                })
                .value(),
            names = _.map(estimates, "name"),
            vals = _.chain(estimates)
                .map(function (d) {
                    let {upper_bound_interval, lower_bound_interval} = d.group.getIntervals();
                    return [d.group.data.estimate, lower_bound_interval, upper_bound_interval];
                })
                .flattenDeep()
                .filter(function (d) {
                    return _.isNumber(d);
                })
                .value(),
            getXDomain = function (scale_type, vals) {
                if (scale_type === "log") {
                    vals = _.filter(vals, function (d) {
                        return d > 0;
                    });
                }
                var domain = d3.extent(vals);
                if (domain[0] === domain[1]) {
                    // set reasonable defaults for domain if there is no domain.
                    if (scale_type === "log") {
                        domain[0] = domain[0] * 0.1;
                        domain[1] = domain[1] * 10;
                    } else {
                        if (domain[0] > 0) {
                            domain[0] = 0;
                        } else if (domain[0] >= -1) {
                            domain[0] = -1;
                        } else {
                            domain[0] = domain[0] * 2;
                        }

                        if (domain[1] >= -1 && domain[1] <= 1) {
                            domain[1] = 1;
                        }
                    }
                }
                return domain;
            };

        _.extend(this, {
            title_str: data.name,
            scale_type: data.metric.isLog ? "log" : "linear",
            estimates,
            lines,
            names,
            x_domain: getXDomain(this.scale_type, vals),
            x_label_text: data.metric.name,
        });
    }

    isPlottable() {
        return this.estimates.length > 0 || this.lines.length > 0;
    }

    set_defaults() {
        _.extend(this, {
            padding: {
                top: 35,
                right: 20,
                bottom: 40,
                left: 20,
                left_original: 20,
            },
            row_height: 30,
            x_axis_settings: {
                scale_type: "linear",
                text_orient: "bottom",
                axis_class: "axis x_axis",
                number_ticks: 6,
                x_translate: 0,
                gridlines: true,
                gridline_class: "primary_gridlines x_gridlines",
                axis_labels: true,
                label_format: undefined,
            },
            y_axis_settings: {
                scale_type: "ordinal",
                text_orient: "left",
                axis_class: "axis y_axis",
                gridlines: true,
                gridline_class: "primary_gridlines y_gridlines",
                axis_labels: true,
                label_format: undefined,
            },
        });
    }

    get_plot_sizes() {
        this.h = this.row_height * this.names.length;
        this.w = this.plot_div.width() - this.padding.right - this.padding.left; // extra for margins
        var menu_spacing = this.options.show_menu_bar ? 40 : 0;
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + menu_spacing + "px",
        });
    }

    add_axes() {
        if (this.scale_type === "log" && this.x_domain[0] >= 1) {
            this.x_domain[0] = 0.1;
        }

        _.extend(this.x_axis_settings, {
            domain: this.x_domain,
            rangeRound: [0, this.w],
            y_translate: this.h,
            scale_type: this.scale_type,
        });

        _.extend(this.y_axis_settings, {
            domain: this.names,
            number_ticks: this.names.length,
            rangeRound: [0, this.h],
            x_translate: 0,
            y_translate: 0,
        });

        this.build_y_axis();
        this.build_x_axis();
    }

    draw_visualizations() {
        var x = this.x_scale,
            y = this.y_scale,
            mid = y.bandwidth() / 2;

        // vertical reference line at 1 relative risk
        this.vis
            .append("line")
            .attr("x1", x(1))
            .attr("y1", 0)
            .attr("x2", x(1))
            .attr("y2", this.h)
            .attr("class", "reference_line");

        // estimate range
        this.estimate_range = this.vis.append("g").attr("class", "estimates_range");
        this.estimate_range
            .selectAll("line.temp")
            .data(this.lines)
            .enter()
            .append("line")
            .attr("x1", function (d) {
                return x(d.lower_bound_interval);
            })
            .attr("y1", function (d) {
                return y(d.name) + mid;
            })
            .attr("x2", function (d) {
                return x(d.upper_bound_interval);
            })
            .attr("y2", function (d) {
                return y(d.name) + mid;
            })
            .attr("class", "dr_err_bars");

        this.estimate_range
            .selectAll("line.temp")
            .data(this.lines)
            .enter()
            .append("line")
            .attr("x1", function (d) {
                return x(d.lower_bound_interval);
            })
            .attr("y1", function (d) {
                return y(d.name) + mid * 1.5;
            })
            .attr("x2", function (d) {
                return x(d.lower_bound_interval);
            })
            .attr("y2", function (d) {
                return y(d.name) + mid * 0.5;
            })
            .attr("class", "dr_err_bars");

        this.estimate_range
            .selectAll("line.temp")
            .data(this.lines)
            .enter()
            .append("line")
            .attr("x1", function (d) {
                return x(d.upper_bound_interval);
            })
            .attr("y1", function (d) {
                return y(d.name) + mid * 1.5;
            })
            .attr("x2", function (d) {
                return x(d.upper_bound_interval);
            })
            .attr("y2", function (d) {
                return y(d.name) + mid * 0.5;
            })
            .attr("class", "dr_err_bars");

        // central estimate
        this.estimates_group = this.vis.append("g").attr("class", "estimates");
        this.estimates = this.estimates_group
            .selectAll("path.dot")
            .data(this.estimates)
            .enter()
            .append("circle")
            .attr("class", "dose_points")
            .attr("r", 7)
            .attr("cx", d => x(d.estimate))
            .attr("cy", d => y(d.name) + mid);
    }

    resize_plot_dimensions() {
        // Resize plot based on the dimensions of the labels.
        var ylabel_width = this.plot_div.find(".y_axis")[0].getBoundingClientRect().width;
        if (this.padding.left < this.padding.left_original + ylabel_width) {
            this.padding.left = this.padding.left_original + ylabel_width;
            this.build_plot();
        }
    }
}

export default ResultForestPlot;
