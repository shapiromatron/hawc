import * as d3 from "d3";
import D3Plot from "shared/utils/D3Plot";
import HAWCUtils from "shared/utils/HAWCUtils";
import $ from "$";

import {applyStyles} from "../summary/common";

class StyleViewer extends D3Plot {
    constructor($plot_div, style, settings) {
        super();
        this.style = style;
        this.settings = settings || StyleViewer.default_settings();
        this.set_defaults();
        this.plot_div = $plot_div;
        if (this.settings.plot_settings.build_plot_startup) {
            this.build_plot();
        }
    }

    static default_settings() {
        return {
            plot_settings: {
                show_menu_bar: false,
                build_plot_startup: true,
                width: 50,
                height: 50,
                padding: {
                    top: 10,
                    right: 10,
                    bottom: 10,
                    left: 10,
                },
            },
        };
    }

    build_plot() {
        this.plot_div.html("");
        this.get_plot_sizes();
        this.build_plot_skeleton(false, "Style preview functionality");
        this.draw_visualizations();
    }

    get_plot_sizes() {
        this.w = this.settings.plot_settings.width;
        this.h = this.settings.plot_settings.height;
        var menu_spacing = this.settings.plot_settings.show_menu_bar ? 40 : 0;
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + menu_spacing + "px",
        });
    }

    set_defaults() {
        this.padding = $.extend({}, this.settings.plot_settings.padding); //copy object

        this.x_axis_settings = {
            domain: [0, 2],
            rangeRound: [0, this.settings.plot_settings.width],
            x_translate: 0,
            y_translate: 0,
            scale_type: "linear",
            text_orient: "bottom",
            axis_class: "axis x_axis",
            gridlines: false,
            gridline_class: "primary_gridlines x_gridlines",
            number_ticks: 10,
            axis_labels: false,
            label_format: undefined,
        };

        this.y_axis_settings = {
            domain: [0, 2],
            rangeRound: [0, this.settings.plot_settings.height],
            number_ticks: 10,
            x_translate: 0,
            y_translate: 0,
            scale_type: "linear",
            text_orient: "left",
            axis_class: "axis y_axis",
            gridlines: false,
            gridline_class: "primary_gridlines y_gridlines",
            axis_labels: false,
            label_format: undefined,
        };
    }

    draw_visualizations() {
        this.build_y_axis();
        this.build_x_axis();

        var x = this.x_scale,
            y = this.y_scale;

        if (this.style.type === "line") {
            this.lines = this.vis
                .selectAll()
                .data([
                    {x1: 0.25, x2: 1.75, y1: 1, y2: 1},
                    {x1: 0.25, x2: 0.25, y1: 0.5, y2: 1.5},
                    {x1: 1.75, x2: 1.75, y1: 0.5, y2: 1.5},
                ])
                .enter()
                .append("svg:line")
                .attr("x1", v => x(v.x1))
                .attr("x2", v => x(v.x2))
                .attr("y1", v => y(v.y1))
                .attr("y2", v => y(v.y2));

            this._update_styles(this.style.settings, false);
        }

        if (this.style.type === "rectangle") {
            this.rectangles = this.vis
                .selectAll()
                .data([{x: 0.25, y: 0.25, width: 1.5, height: 1.5}])
                .enter()
                .append("svg:rect")
                .attr("x", v => x(v.x))
                .attr("y", v => x(v.y))
                .attr("width", v => y(v.width))
                .attr("height", v => y(v.height));

            this._update_styles(this.style.settings, false);
        }

        if (this.style.type === "symbol") {
            this.symbol = this.vis
                .selectAll("path")
                .data([
                    {x: 0.5, y: 0.5},
                    {x: 1.5, y: 0.5},
                    {x: 1.5, y: 1.5},
                    {x: 0.5, y: 1.5},
                ])
                .enter()
                .append("path")
                .attr("d", d3.symbol())
                .attr("transform", d => `translate(${x(d.x)},${y(d.y)})`)
                .on("click", () => this._update_styles(this.style.settings, true));

            this._update_styles(this.style.settings, false);
        }

        if (this.style.type === "text") {
            this.lines = this.vis
                .selectAll()
                .data([
                    {x1: 1.25, x2: 0.75, y1: 1, y2: 1},
                    {x1: 1, x2: 1, y1: 1.25, y2: 0.75},
                ])
                .enter()
                .append("svg:line")
                .attr("x1", v => x(v.x1))
                .attr("x2", v => x(v.x2))
                .attr("y1", v => y(v.y1))
                .attr("y2", v => y(v.y2))
                .attr("stroke-width", 2)
                .attr("stroke", "#ccc");

            this.text = this.vis.append("svg:text").attr("x", x(1)).attr("y", y(1)).text("text");

            this._update_styles(this.style.settings, false);
        }

        if (this.style.type == "legend") {
            if (this.settings.line_style) this.add_legend_lines();
            if (this.settings.line_style) this.add_legend_symbols();
            this._update_styles(this.style, false);
        }
    }

    add_legend_lines() {
        var x = this.x_scale,
            y = this.y_scale;

        this.lines = this.vis
            .selectAll()
            .data([
                {x1: 0.25, x2: 1.75, y1: 1, y2: 1},
                {x1: 0.25, x2: 0.25, y1: 0.5, y2: 1.5},
                {x1: 1.75, x2: 1.75, y1: 0.5, y2: 1.5},
            ])
            .enter()
            .append("svg:line")
            .attr("x1", v => x(v.x1))
            .attr("x2", v => x(v.x2))
            .attr("y1", v => y(v.y1))
            .attr("y2", v => y(v.y2));
    }

    add_legend_rects() {
        var x = this.x_scale,
            y = this.y_scale;

        this.rectangles = this.vis
            .selectAll()
            .data([{min: 0.1, max: 1.9}])
            .enter()
            .append("svg:rect")
            .attr("x", d => x(d.min))
            .attr("y", d => y(d.min))
            .attr("width", d => x(d.max) - x(d.min))
            .attr("height", d => y(d.max) - y(d.min));
    }

    add_legend_symbols() {
        var x = this.x_scale,
            y = this.y_scale;

        this.symbol = this.vis
            .selectAll("path")
            .data([{x: 1, y: 1}])
            .enter()
            .append("path")
            .attr("d", d3.symbol())
            .attr("transform", d => `translate(${x(d.x)},${y(d.y)})`);
    }

    _update_styles(style_settings, randomize_position) {
        var x = this.x_scale,
            y = this.y_scale;

        if (this.style.type === "line") {
            this.lines
                .transition()
                .duration(1000)
                .call(selection => applyStyles(this.svg, selection, style_settings));
        }

        var randomize_data = function () {
            return [
                {x: Math.random() * 2, y: Math.random() * 2},
                {x: Math.random() * 2, y: Math.random() * 2},
                {x: Math.random() * 2, y: Math.random() * 2},
                {x: Math.random() * 2, y: Math.random() * 2},
            ];
        };

        if (this.style.type === "symbol") {
            var d = randomize_position ? randomize_data() : this.symbol.data();

            this.symbol
                .data(d)
                .transition()
                .duration(1000)
                .attr("transform", d => `translate(${x(d.x)},${y(d.y)})`)
                .attr(
                    "d",
                    d3
                        .symbol()
                        .size(style_settings.size)
                        .type(HAWCUtils.symbolStringToType(style_settings.type))
                )
                .call(selection => applyStyles(this.svg, selection, style_settings));
        }

        if (this.style.type === "text") {
            this.text.attr("transform", undefined);
            this.text
                .transition()
                .duration(1000)
                .attr("font-size", style_settings["font-size"])
                .attr("font-weight", style_settings["font-weight"])
                .attr("fill-opacity", style_settings["fill-opacity"])
                .attr("text-anchor", style_settings["text-anchor"])
                .attr("fill", style_settings.fill)
                .attr("transform", `rotate(${style_settings.rotate} 25,25)`);
        }

        if (this.style.type === "rectangle") {
            this.rectangles
                .transition()
                .duration(1000)
                .call(selection => applyStyles(this.svg, selection, style_settings));
        }

        if (this.style.type === "legend") {
            if (style_settings.rect_style) {
                if (!this.rectangles) this.add_legend_rects();
                this.rectangles
                    .transition()
                    .duration(1000)
                    .call(selection =>
                        applyStyles(this.svg, selection, style_settings.rect_style.settings)
                    );
            } else {
                if (this.rectangles) {
                    this.rectangles.remove();
                    delete this.rectangles;
                }
            }

            if (style_settings.line_style) {
                if (!this.lines) this.add_legend_lines();
                this.lines
                    .transition()
                    .duration(1000)
                    .call(selection =>
                        applyStyles(this.svg, selection, style_settings.line_style.settings)
                    );
            } else {
                if (this.lines) {
                    this.lines.remove();
                    delete this.lines;
                }
            }

            if (style_settings.symbol_style) {
                if (!this.symbol) this.add_legend_symbols();
                this.symbol
                    .transition()
                    .duration(1000)
                    .attr("transform", d => `translate(${x(d.x)},${y(d.y)})`)
                    .attr(
                        "d",
                        d3
                            .symbol()
                            .size(style_settings.symbol_style.settings.size)
                            .type(
                                HAWCUtils.symbolStringToType(
                                    style_settings.symbol_style.settings.type
                                )
                            )
                    )
                    .call(selection =>
                        applyStyles(this.svg, selection, style_settings.symbol_style.settings)
                    );
            } else {
                if (this.symbol) {
                    this.symbol.remove();
                    delete this.symbol;
                }
            }
        }
    }

    apply_new_styles(style_settings, randomize_position) {
        // don't change the object, just the styles rendered in viewer
        this._update_styles(style_settings, randomize_position);
    }

    update_style_object(style) {
        // change the style object
        this.style = style;
        this._update_styles(this.style.settings, true);
    }
}

export default StyleViewer;
