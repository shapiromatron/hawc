import * as d3 from "d3";
import _ from "lodash";

import $ from "$";

import D3Visualization from "./D3Visualization";

class EndpointAggregationForestPlot extends D3Visualization {
    constructor(_parent, _data, _options) {
        super(...arguments);
        this.setDefaults();
    }

    setDefaults() {
        this.padding = {top: 40, right: 20, bottom: 40, left: 30};
        this.padding.left_original = this.padding.left;
        this.buff = 0.05; // addition numerical-spacing around dose/response units
    }

    render($div) {
        this.plot_div = $div;
        this.processData();
        this.build_plot_skeleton(true, "An exposure response forest plot");
        this.add_title();
        this.add_axes();
        this.add_endpoint_lines();
        this.add_dose_points();
        this.add_axis_text();
        this.add_final_rectangle();
        this.build_x_label();
        this.build_y_label();
        this.add_legend();
        this.resize_plot_dimensions();
        this.trigger_resize();
        if (this.menu_div) {
            this.menu_div.remove();
            delete this.menu_div;
        }
        this.add_menu();
        this.add_menu_button(this.parent.addPlotToggleButton());
    }

    processData() {
        var points = [],
            lines = [],
            endpoint_labels = [],
            y = 0,
            val,
            control,
            lower_ci,
            upper_ci,
            egs,
            getCoordClass = function (e, i) {
                if (e.data.LOEL == i) return "LOEL";
                if (e.data.NOEL == i) return "NOEL";
                return "";
            },
            dose_units = this.data.endpoints[0].dose_units;

        _.chain(this.data.endpoints)
            .filter(function (e) {
                return e.hasEGdata();
            })
            .each(function (e) {
                const shortCitation = e.data.animal_group.experiment.study.short_citation,
                    experimentName = e.data.animal_group.experiment.name,
                    animalGroup = e.data.animal_group.name,
                    endpointName = e.data.name;
                egs = _.filter(e.data.groups, d => d.isReported);
                endpoint_labels.push({
                    endpoint: e,
                    y: y + egs.length * 0.5,
                    label: `${shortCitation}- ${experimentName}- ${animalGroup}: ${endpointName}`,
                });

                egs.forEach(function (eg, i) {
                    var txt = [
                        e.data.animal_group.experiment.study.short_citation,
                        e.data.name,
                        "Dose: " + eg.dose,
                        "N: " + eg.n,
                    ];

                    if (i === 0) {
                        // get control value
                        if (e.data.data_type == "C") {
                            control = parseFloat(eg.response, 10);
                        } else {
                            control = parseFloat(eg.incidence / eg.n, 10);
                        }
                        if (control === 0) {
                            control = 1e-10;
                        }
                    }

                    // get plot value
                    y += 1;
                    if (e.data.data_type == "C") {
                        txt.push("Mean: " + eg.response, "Stdev: " + eg.stdev);
                        val = (eg.response - control) / control;
                        lower_ci = (eg.lower_ci - control) / control;
                        upper_ci = (eg.upper_ci - control) / control;
                    } else {
                        txt.push("Incidence: " + eg.incidence);
                        val = eg.incidence / eg.n;
                        lower_ci = eg.lower_ci;
                        upper_ci = eg.upper_ci;
                    }
                    points.push({
                        x: val,
                        y,
                        class: getCoordClass(e, i),
                        text: txt.join("\n"),
                        dose: eg.dose,
                        lower_ci,
                        upper_ci,
                        endpoint: e,
                    });
                });
                y += 1;
                lines.push({y, endpoint: e.data.name});
            })
            .value();

        // remove final spacer-line
        lines.pop();
        y -= 1;

        // calculate dimensions
        var plot_width = parseInt(
                this.plot_div.width() - this.padding.right - this.padding.left,
                10
            ),
            plot_height = parseInt(points.length * 20, 10),
            container_height = parseInt(
                plot_height + this.padding.top + this.padding.bottom + 45,
                10
            );

        // set settings to object
        _.extend(this, {
            points,
            lines,
            endpoint_labels,
            min_x: d3.min(points, function (v) {
                return v.lower_ci;
            }),
            max_x: d3.max(points, function (v) {
                return v.upper_ci;
            }),
            min_y: 0,
            max_y: (y += 1),
            w: plot_width,
            h: plot_height,
            title_str: this.data.title,
            x_label_text: "% change from control (continuous), % incidence (dichotomous)",
            y_label_text: `Doses (${dose_units})`,
        });
        this.plot_div.css({height: `${container_height}px`});
    }

    add_axes() {
        // using plot-settings, customize axes
        this.x_axis_settings = {
            scale_type: "linear",
            domain: [this.min_x - this.max_x * this.buff, this.max_x * (1 + this.buff)],
            rangeRound: [0, this.w],
            text_orient: "bottom",
            x_translate: 0,
            y_translate: this.h,
            axis_class: "axis x_axis",
            gridlines: true,
            gridline_class: "primary_gridlines x_gridlines",
            number_ticks: 10,
            axis_labels: true,
            label_format: d3.format(".0%"),
        };

        this.y_axis_settings = {
            scale_type: "linear",
            domain: [this.max_y, this.min_y], // invert axis
            rangeRound: [this.h, 0],
            text_orient: "left",
            x_translate: 0,
            y_translate: 0,
            axis_class: "axis y_axis",
            gridlines: false,
            gridline_class: "primary_gridlines y_gridlines",
            number_ticks: 10,
            axis_labels: false,
            label_format: undefined, // default
        };
        this.build_x_axis();
        this.build_y_axis();
    }

    resize_plot_dimensions() {
        // Resize plot based on the dimensions of the labels.
        var ylabel_width =
            d3.max(
                this.plot_div.find(".forest_plot_labels").map(function () {
                    return this.getComputedTextLength();
                })
            ) +
            d3.max(
                this.plot_div.find(".dr_tick_text").map(function () {
                    return this.getComputedTextLength();
                })
            );
        if (this.padding.left < this.padding.left_original + ylabel_width) {
            this.padding.left = this.padding.left_original + ylabel_width;
            this.render(this.plot_div);
        }
    }

    add_endpoint_lines() {
        // horizontal line separators between endpoints
        var x = this.x_scale,
            y = this.y_scale;

        //horizontal lines
        this.vis
            .selectAll("svg.endpoint_lines")
            .data(this.lines)
            .enter()
            .append("line")
            .attr("x1", function (_d) {
                return x(x.domain()[0]);
            })
            .attr("y1", function (d) {
                return y(d.y);
            })
            .attr("x2", function (_d) {
                return x(x.domain()[1]);
            })
            .attr("y2", function (d) {
                return y(d.y);
            })
            .attr("class", "primary_gridlines");

        // add vertical line at zero
        this.vis
            .append("line")
            .attr("x1", this.x_scale(0))
            .attr("y1", this.y_scale(this.min_y))
            .attr("x2", this.x_scale(0))
            .attr("y2", this.y_scale(this.max_y))
            .attr("class", "reference_line");
    }

    add_dose_points() {
        var x = this.x_scale,
            y = this.y_scale,
            lines = this.points.filter(function (v) {
                return $.isNumeric(v.lower_ci) && $.isNumeric(v.upper_ci);
            }),
            points = this.points.filter(function (v) {
                return $.isNumeric(v.x);
            });

        // horizontal confidence interval line
        this.vis
            .selectAll("svg.error_bars")
            .data(lines)
            .enter()
            .append("line")
            .attr("x1", d => x(d.lower_ci))
            .attr("y1", d => y(d.y))
            .attr("x2", d => x(d.upper_ci))
            .attr("y2", d => y(d.y))
            .attr("class", "dr_err_bars");

        // lower vertical vertical confidence intervals line
        this.vis
            .selectAll("svg.error_bars")
            .data(lines)
            .enter()
            .append("line")
            .attr("x1", d => x(d.lower_ci))
            .attr("y1", d => y(d.y) - 5)
            .attr("x2", d => x(d.lower_ci))
            .attr("y2", d => y(d.y) + 5)
            .attr("class", "dr_err_bars");

        // upper vertical confidence intervals line
        this.vis
            .selectAll("svg.error_bars")
            .data(lines)
            .enter()
            .append("line")
            .attr("x1", d => x(d.upper_ci))
            .attr("y1", d => y(d.y) - 5)
            .attr("x2", d => x(d.upper_ci))
            .attr("y2", d => y(d.y) + 5)
            .attr("class", "dr_err_bars");

        // central tendency of percent-change
        this.dots = this.vis
            .selectAll("path.dot")
            .data(points)
            .enter()
            .append("circle")
            .attr("r", "7")
            .attr("class", d => "dose_points " + d.class)
            .style("cursor", "pointer")
            .attr("transform", d => `translate(${x(d.x)},${y(d.y)})`)
            .on("click", (_event, d) => d.endpoint.displayAsModal());

        // add the outer element last
        this.dots.append("svg:title").text(d => d.text);
    }

    add_axis_text() {
        // Next set labels on axis
        var y_scale = this.y_scale;
        this.y_dose_text = this.vis
            .selectAll("y_axis.text")
            .data(this.points)
            .enter()
            .append("text")
            .attr("x", -5)
            .attr("y", function (v, _i) {
                return y_scale(v.y);
            })
            .attr("dy", "0.5em")
            .attr("class", "dr_tick_text")
            .attr("text-anchor", "end")
            .text(function (d, _i) {
                return d.dose;
            });

        this.labels = this.vis
            .selectAll("y_axis.text")
            .data(this.endpoint_labels)
            .enter()
            .append("text")
            .attr("x", -this.padding.left + 25)
            .attr("y", function (v, _i) {
                return y_scale(v.y);
            })
            .attr("class", "dr_title forest_plot_labels")
            .attr("text-anchor", "start")
            .style("cursor", "pointer")
            .text(function (d, _i) {
                return d.label;
            })
            .on("click", function (_event, v) {
                v.endpoint.displayAsModal();
            });
    }

    add_legend() {
        var addItem = function (txt, cls, color) {
                return {
                    text: txt,
                    classes: cls,
                    color,
                };
            },
            item_height = 20,
            box_w = 110,
            items = [addItem("Doses", "dose_points")],
            noel_names = this.data.endpoints[0].data.noel_names;

        if (this.plot_div.find(".NOEL").length > 0)
            items.push(addItem(noel_names.noel, "dose_points NOEL"));
        if (this.plot_div.find(".LOEL").length > 0)
            items.push(addItem(noel_names.loel, "dose_points LOEL"));
        if (this.plot_div.find(".BMDL").length > 0) items.push(addItem("BMDL", "dose_points BMDL"));

        this.build_legend({
            items,
            item_height,
            box_w,
            box_h: items.length * item_height,
            box_l: this.w + this.padding.right - box_w - 10,
            dot_r: 5,
            box_t: 10 - this.padding.top,
            box_padding: 5,
        });
    }
}

export default EndpointAggregationForestPlot;
