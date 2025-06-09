import * as d3 from "d3";
import _ from "lodash";
import h from "shared/utils/helpers";

import $ from "$";

import D3Visualization from "./D3Visualization";

class EndpointAggregationExposureResponsePlot extends D3Visualization {
    constructor(_parent, _data, _options) {
        super(...arguments);
        this.setDefaults();
    }

    setDefaults() {
        var left = 25;

        _.extend(this, {
            default_x_scale: "log",
            padding: {
                top: 40,
                right: 20,
                bottom: 40,
                left,
                left_original: left,
            },
            buff: 0.05,
            x_axis_settings: {
                scale_type: this.options.default_x_axis || "log",
                text_orient: "bottom",
                axis_class: "axis x_axis",
                gridlines: true,
                gridline_class: "primary_gridlines x_gridlines",
                number_ticks: 10,
                axis_labels: true,
                label_format: h.numericAxisFormat,
            },
            y_axis_settings: {
                scale_type: "ordinal",
                text_orient: "left",
                axis_class: "axis y_axis",
                gridlines: true,
                gridline_class: "primary_gridlines y_gridlines",
                axis_labels: true,
                label_format: undefined, //default
            },
        });
    }

    render($div) {
        this.plot_div = $div;
        this.processData();
        this.build_plot_skeleton(true, "An exposure response array");
        this.add_title();
        this.add_axes();
        this.build_x_label();
        this.build_y_label();
        this.add_dose_lines();
        this.add_dose_points();
        this.add_final_rectangle();
        this.add_legend();
        this.customize_menu();
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
        var min = Infinity,
            max = -Infinity,
            default_x_scale = this.default_x_scale,
            lines_data = [],
            points_data = [],
            dose_units = this.data.endpoints[0].doseUnits.activeUnit;

        this.data.endpoints
            .filter(d => d.data.groups.length > 0)
            .forEach(function (e) {
                let bmd = e.get_special_bmd_value("BMD"),
                    bmdl = e.get_special_bmd_value("BMDL"),
                    egs = e.data.groups;

                // get min/max information
                min =
                    default_x_scale == "log"
                        ? Math.min(min, egs[1].dose)
                        : Math.min(min, egs[0].dose);
                max = Math.max(max, egs[egs.length - 1].dose);
                if (isFinite(bmdl)) {
                    min = Math.min(min, bmdl);
                    max = Math.max(max, bmdl);
                }

                //setup lines information for dose-response line (excluding control)
                const shortCitation = e.data.animal_group.experiment.study.short_citation,
                    experimentName = e.data.animal_group.experiment.name,
                    animalGroup = e.data.animal_group.name,
                    endpointName = e.data.name;

                lines_data.push({
                    y: e.data.id,
                    name: `${shortCitation}- ${experimentName}- ${animalGroup}: ${endpointName}`,
                    x_lower: egs[1].dose,
                    x_upper: egs[egs.length - 1].dose,
                });

                // setup points information

                // add LOEL/NOEL
                egs.forEach(function (v2, i2) {
                    var txt = [
                        e.data.animal_group.experiment.study.short_citation,
                        e.data.name,
                        `Dose: ${v2.dose}`,
                        `N: ${v2.n}`,
                    ];
                    if (v2.dose > 0) {
                        if (e.data.data_type == "C") {
                            txt.push(`Mean: ${v2.response}\nStdev: ${v2.stdev}`);
                        } else {
                            txt.push(`Incidence: ${v2.incidence}`);
                        }
                        var coords = {
                            endpoint: e,
                            x: v2.dose,
                            y: e.data.id,
                            classes: "",
                            text: txt.join("\n"),
                        };
                        if (e.data.LOEL == i2) {
                            coords.classes = "LOEL";
                        }
                        if (e.data.NOEL == i2) {
                            coords.classes = "NOEL";
                        }
                        points_data.push(coords);
                    }
                });
                // add BMDL
                if (isFinite(bmdl)) {
                    var txt = [
                        e.data.animal_group.experiment.study.short_citation,
                        e.data.name,
                        `BMD: ${bmd}`,
                        `BMDL: ${bmdl}`,
                    ];

                    points_data.push({
                        endpoint: e,
                        x: bmdl,
                        y: e.data.id,
                        classes: "BMDL",
                        text: txt.join("\n"),
                    });
                }
            });

        // calculate dimensions
        var plot_width = parseInt(
                this.plot_div.width() - this.padding.right - this.padding.left - 20,
                10
            ),
            plot_height = parseInt(lines_data.length * 40, 10),
            container_height = parseInt(
                plot_height + this.padding.top + this.padding.bottom + 45,
                10
            );

        _.extend(this, {
            lines_data,
            points_data,
            min_x: min,
            max_x: max,
            min_y: 0,
            max_y: lines_data.length,
            w: plot_width,
            h: plot_height,
            title_str: this.data.title,
            x_label_text: `Dose (${dose_units.name})`,
            y_label_text: "Endpoints",
        });
        this.plot_div.css({height: `${container_height}px`});
    }

    toggle_x_axis() {
        if (window.event && window.event.stopPropagation) {
            event.stopPropagation();
        }
        if (this.x_axis_settings.scale_type == "linear") {
            this.x_axis_settings.scale_type = "log";
            this.x_axis_settings.number_ticks = 1;
            this.x_axis_settings.label_format = h.numericAxisFormat;
        } else {
            this.x_axis_settings.scale_type = "linear";
            this.x_axis_settings.number_ticks = 10;
            this.x_axis_settings.label_format = undefined;
        }
        this.update_x_domain();
        this.x_scale = this._build_scale(this.x_axis_settings);
        this.x_axis_change_chart_update();
    }

    x_axis_change_chart_update() {
        // Assuming the plot has already been constructed once,
        // rebuild plot with updated x-scale.
        var x = this.x_scale;

        //rebuild x-axis
        this.xAxis
            .scale(this.x_scale)
            .ticks(this.x_axis_settings.number_ticks, this.x_axis_settings.label_format);

        this.vis.selectAll(".x_axis").transition().duration(1000).call(this.xAxis);

        this.rebuild_x_gridlines({animate: true});

        //rebuild dosing lines
        this.dosing_lines
            .selectAll("line")
            .transition()
            .duration(1000)
            .attr("x1", d => x(d.x_lower))
            .attr("x2", d => x(d.x_upper));

        this.dots
            .transition()
            .duration(1000)
            .attr("cx", d => x(d.x));
    }

    resize_plot_dimensions() {
        // Resize plot based on the dimensions of the labels.
        var ylabel_width = this.vis.select(".y_axis").node().getBoundingClientRect().width;
        if (this.padding.left < this.padding.left_original + ylabel_width) {
            this.padding.left = this.padding.left_original + ylabel_width;
            this.render(this.plot_div);
        }
    }

    add_axes() {
        // using plot-settings, customize axes
        this.update_x_domain();
        $.extend(this.x_axis_settings, {
            rangeRound: [0, this.w],
            x_translate: 0,
            y_translate: this.h,
        });

        $.extend(this.y_axis_settings, {
            domain: this.lines_data.map(d => d.y),
            rangeRound: [0, this.h],
            number_ticks: this.lines_data.length,
            x_translate: 0,
            y_translate: 0,
        });
        this.build_x_axis();
        this.build_y_axis();

        var lines_data = this.lines_data;
        d3.select(this.svg)
            .selectAll(".y_axis text")
            .text(function (v, _i) {
                var name;
                lines_data.forEach(function (endpoint) {
                    if (v === endpoint.y) {
                        name = endpoint.name;
                        return;
                    }
                });
                return name;
            });
    }

    update_x_domain() {
        var domain_value;
        if (this.x_axis_settings.scale_type === "linear") {
            domain_value = [this.min_x - this.max_x * this.buff, this.max_x * (1 + this.buff)];
        } else {
            domain_value = [this.min_x, this.max_x];
        }
        this.x_axis_settings.domain = domain_value;
    }

    add_dose_lines() {
        var x = this.x_scale,
            y = this.y_scale,
            halfway = y.bandwidth() / 2;

        this.dosing_lines = this.vis.append("g");
        this.dosing_lines
            .selectAll("line")
            .data(this.lines_data)
            .enter()
            .append("line")
            .attr("x1", d => x(d.x_lower))
            .attr("x2", d => x(d.x_upper))
            .attr("y1", d => y(d.y) + halfway)
            .attr("y2", d => y(d.y) + halfway)
            .attr("class", "dr_err_bars"); // todo: rename class to more general name
    }

    add_dose_points() {
        var x = this.x_scale,
            y = this.y_scale,
            tt_width = 400,
            halfway = y.bandwidth() / 2;

        var tooltip = d3
            .select("body")
            .append("div")
            .attr("class", "d3modal")
            .attr("width", tt_width + "px")
            .style("position", "absolute")
            .style("z-index", "1000")
            .style("visibility", "hidden")
            .on("click", function () {
                $(this).css("visibility", "hidden");
            });
        this.tooltip = $(tooltip[0]);

        this.dots_group = this.vis.append("g");
        this.dots = this.dots_group
            .selectAll("circle")
            .data(this.points_data)
            .enter()
            .append("circle")
            .attr("r", "7")
            .attr("class", d => `dose_points ${d.classes}`)
            .attr("cursor", "pointer")
            .attr("cx", d => x(d.x))
            .attr("cy", d => y(d.y) + halfway)
            .style("cursor", "pointer")
            .on("click", (_event, v) => v.endpoint.displayAsModal());

        // add the outer element last
        this.dots.append("svg:title").text(d => d.text);
    }

    customize_menu() {
        this.add_menu();
        this.add_menu_button(this.parent.addPlotToggleButton());
        this.add_menu_button({
            id: "toggle_x_axis",
            cls: "btn btn-sm",
            title: "Change x-axis scale (shortcut: click the x-axis label)",
            text: "",
            icon: "fa fa-arrows-h",
            on_click: this.toggle_x_axis.bind(this),
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

        if (this.plot_div.find(".NOEL").length > 0) {
            items.push(addItem(noel_names.noel, "dose_points NOEL"));
        }

        if (this.plot_div.find(".LOEL").length > 0) {
            items.push(addItem(noel_names.loel, "dose_points LOEL"));
        }

        if (this.plot_div.find(".BMDL").length > 0) {
            items.push(addItem("BMDL", "dose_points BMDL"));
        }

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

export default EndpointAggregationExposureResponsePlot;
