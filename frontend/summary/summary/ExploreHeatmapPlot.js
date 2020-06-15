import _ from "lodash";
import d3 from "d3";
import {autorun, toJS} from "mobx";
import D3Visualization from "./D3Visualization";
import h from "shared/utils/helpers";
import HAWCModal from "utils/HAWCModal";

import React from "react";
import ReactDOM from "react-dom";
import HeatmapDatastore from "./heatmap/HeatmapDatastore";
import DatasetTable from "./heatmap/DatasetTable";
import FilterWidgetContainer from "./heatmap/FilterWidgetContainer";
import Tooltip from "./heatmap/Tooltip";

class ExploreHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        super(...arguments);
        this.modal = new HAWCModal();
        this.store = new HeatmapDatastore(data.settings, data.dataset);
        this.dataset = data.dataset;
        this.settings = data.settings;
        this.generate_properties();
    }

    render($div) {
        // Create svg container
        $div.html(`<div class="row-fluid">
            <div class="span9 heatmap-viz"></div>
            <div class="span3 heatmap-filters"></div>
            <div class="span9 heatmap-tables"></div>
            <div style="position:absolute;" id="exp_heatmap_tooltip"></div>
        </div>`);

        const viz = $div.find(".heatmap-viz")[0],
            tbl = $div.find(".heatmap-tables")[0],
            filters = $div.find(".heatmap-filters")[0];

        this.plot_div = $(viz);
        this.build_plot();
        this.add_grid();
        this.set_trigger_resize();
        this.add_menu();
        ReactDOM.render(<DatasetTable store={this.store} />, tbl);
        ReactDOM.render(<FilterWidgetContainer store={this.store} />, filters);
    }

    set_trigger_resize() {
        var self = this,
            w = this.w + this.settings.padding.left + this.settings.padding.right,
            h = this.h + this.settings.padding.top + this.settings.padding.bottom,
            chart = $(this.svg),
            container = chart.parent();

        this.full_width = w;
        this.full_height = h;
        this.isFullSize = true;
        this.trigger_resize = function(forceResize) {
            var targetWidth = Math.min(container.width(), self.full_width),
                aspect = self.full_width / self.full_height;
            if (forceResize === true && !self.isFullSize) targetWidth = self.full_width;

            if (targetWidth !== self.full_width) {
                // use custom smaller size
                chart.attr("width", targetWidth);
                chart.attr("height", Math.round(targetWidth / aspect));
                self.isFullSize = false;
                if (self.resize_button) {
                    self.resize_button.attr("title", "zoom figure to full-size");
                    self.resize_button.find("i").attr("class", "icon-zoom-in");
                }
            } else {
                // set back to full-size
                chart.attr("width", self.full_width);
                chart.attr("height", self.full_height);
                self.isFullSize = true;
                if (self.resize_button) {
                    self.resize_button.attr("title", "zoom figure to fit screen");
                    self.resize_button.find("i").attr("class", "icon-zoom-out");
                }
            }
        };
        $(window).resize(this.trigger_resize);
        this.trigger_resize(false);
    }

    generate_properties() {
        // `this.padding` required for D3Plot
        this.padding = this.settings.padding;

        this.x_domain = this.settings.x_fields.map(e => _.keys(this.store.intersection[e.column]));
        this.y_domain = this.settings.y_fields.map(e => _.keys(this.store.intersection[e.column]));
        this.x_steps = this.store.scales.x.length;
        this.y_steps = this.store.scales.y.length;

        this.w = this.settings.cell_width * this.x_steps;
        this.h = this.settings.cell_height * this.y_steps;

        // set colorscale
        this.color_scale = d3.scale
            .linear()
            .domain([0, d3.max(this.store.matrixDataset, d => d.rows.length)])
            .range(this.settings.color_range);
    }

    bind_tooltip(selection, type) {
        let tooltip_x_offset = 20,
            tooltip_y_offset = 20;
        selection
            .on("mouseenter", d => {
                $("#exp_heatmap_tooltip").css("display", "block");
                ReactDOM.render(<Tooltip data={d} type={type} />, $("#exp_heatmap_tooltip")[0]);
            })
            .on("mousemove", d =>
                $("#exp_heatmap_tooltip").css({
                    top: `${d3.event.pageY + tooltip_y_offset}px`,
                    left: `${d3.event.pageX + tooltip_x_offset}px`,
                })
            )
            .on("mouseleave", d => $("#exp_heatmap_tooltip").css("display", "none"));
    }

    get_matching_cells(property, filters) {
        let filtered_selection = this.cells_data.filter(d => {
            for (const filter of filters) {
                let included = false;
                for (const cell_filter of d[property]) {
                    if (_.isMatch(cell_filter, filter)) included = true;
                }
                if (!included) return false;
            }
            return true;
        });
        return filtered_selection.data();
    }

    select_cells(selection) {}

    build_axes() {
        let generate_ticks = (domain, fields) => {
                let ticks = [];

                for (let i = 0; i < domain.length; i++) {
                    let tick = domain[i].map(e => {
                        return {label: e, filters: [{[fields[i].column]: e}]};
                    });
                    if (i == 0) {
                        ticks.push(tick);
                    } else {
                        tick = ticks[i - 1]
                            .map(a =>
                                tick.map(b => {
                                    return _.assign({}, b, {filters: b.filters.concat(a.filters)});
                                })
                            )
                            .flat();
                        ticks.push(tick);
                    }
                }
                return ticks;
            },
            x_domains = generate_ticks(this.x_domain, toJS(this.settings.x_fields)).reverse(),
            y_domains = generate_ticks(this.y_domain, toJS(this.settings.y_fields)).reverse(),
            x_axis_offset = 0,
            y_axis_offset = 0,
            label_padding = 6,
            self = this;

        /// Build x axes
        // For each axis...
        for (let i = 0; i < x_domains.length; i++) {
            let axis = this.vis
                    .append("g")
                    .attr("transform", `translate(0,${this.h + x_axis_offset})`),
                domain = x_domains[i],
                band = this.w / domain.length,
                mid = band / 2,
                max = 0;
            // For each tick...
            for (let j = 0; j < domain.length; j++) {
                let label = axis.append("g");
                label
                    .append("text")
                    .attr("transform", `rotate(${this.settings.x_rotate})`)
                    .text(domain[j].label);
                let box = label.node().getBBox(),
                    label_offset = mid - box.width / 2;
                label.attr(
                    "transform",
                    `translate(${label_offset - box.x},${label_padding - box.y})`
                );
                max = Math.max(box.height, max);
                mid += band;
            }
            max += label_padding * 2;
            this.settings.padding.bottom += max;
            x_axis_offset += max;

            // Adds a box around tick labels
            let bbox_group = axis.append("g");
            for (let j = 0; j < domain.length; j++) {
                let bbox = bbox_group
                    .append("polyline")
                    .datum(domain[j])
                    .attr(
                        "points",
                        `${band * j},${max} ${band * j},0 ${band * (j + 1)},0 ${band *
                            (j + 1)},${max}`
                    )
                    .attr("fill", "transparent")
                    .attr("stroke", this.settings.show_axis_border ? "black" : null)
                    .on("click", d => {
                        const cells = self.get_matching_cells("x_filters", d.filters);
                        this.store.setTableDataFilters(new Set(cells));
                    });

                this.bind_tooltip(bbox, "axis");
            }
        }

        /// Build y axes
        // For each axis...
        for (let i = 0; i < y_domains.length; i++) {
            let axis = this.vis.append("g").attr("transform", `translate(${-y_axis_offset},0)`),
                domain = y_domains[i],
                band = this.h / domain.length,
                mid = band / 2,
                max = 0;
            // For each tick...
            for (let j = 0; j < domain.length; j++) {
                let label = axis.append("g");
                label
                    .append("text")
                    .attr("transform", `rotate(${this.settings.y_rotate})`)
                    .text(domain[j].label);
                let box = label.node().getBBox(),
                    label_offset = mid - box.height / 2;
                label.attr(
                    "transform",
                    `translate(${-box.width - box.x - label_padding},${label_offset - box.y})`
                );
                max = Math.max(box.width, max);
                mid += band;
            }
            max += label_padding * 2;
            this.settings.padding.left += max;
            y_axis_offset += max;

            // Adds a box around tick labels
            let bbox_group = axis.append("g");
            for (let j = 0; j < domain.length; j++) {
                let bbox = bbox_group
                    .append("polyline")
                    .datum(domain[j])
                    .attr(
                        "points",
                        `${-max},${band * j} 0,${band * j} 0,${band * (j + 1)} ${-max},${band *
                            (j + 1)}`
                    )
                    .attr("fill", "transparent")
                    .attr("stroke", this.settings.show_axis_border ? "black" : null)
                    .on("click", d => {
                        const cells = this.get_matching_cells("y_filters", d.filters);
                        this.store.setTableDataFilters(new Set(cells));
                    });
                this.bind_tooltip(bbox, "axis");
            }
        }
    }

    add_grid() {
        if (!this.settings.show_grid) {
            return;
        }
        // Draws lines on plot
        let grid = this.vis.append("g"),
            x_band = this.w / this.x_steps,
            y_band = this.h / this.y_steps;

        grid.selectAll("g.none")
            .data(_.range(this.x_steps + 1))
            .enter()
            .append("line")
            .attr("x1", i => x_band * i)
            .attr("y1", 0)
            .attr("x2", i => x_band * i)
            .attr("y2", this.h)
            .style("stroke", "black");

        grid.selectAll("g.none")
            .data(_.range(this.y_steps + 1))
            .enter()
            .append("line")
            .attr("x1", 0)
            .attr("y1", i => y_band * i)
            .attr("x2", this.w)
            .attr("y2", i => y_band * i)
            .style("stroke", "black");
    }

    build_labels() {
        this.label_margin = 50;

        // Plot title
        if (this.settings.plot_title.length > 0) {
            this.vis
                .append("text")
                .attr("id", "exp_heatmap_title")
                .attr("class", "exp_heatmap_label")
                .attr("x", this.w / 2)
                .attr("y", -this.label_margin / 2)
                .text(this.settings.plot_title);
            this.settings.padding.top += this.label_margin;
        }

        // X axis
        if (this.settings.x_label.length > 0) {
            this.settings.padding.bottom += this.label_margin;
            this.vis
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr("x", this.w / 2)
                .attr("y", this.h + this.settings.padding.bottom - this.label_margin / 2)
                .text(this.settings.x_label);
        }
        // Y axis
        if (this.settings.y_label.length > 0) {
            this.settings.padding.left += this.label_margin;
            this.vis
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr("x", 0)
                .attr("y", 0)
                .attr(
                    "transform",
                    `translate(${-(this.settings.padding.left - this.label_margin / 2)},${this.h /
                        2}) rotate(-90)`
                )
                .text(this.settings.y_label);
        }
    }

    update_plot = data => {
        const self = this,
            tooltip_x_offset = 20,
            tooltip_y_offset = 20;

        this.cells_data = this.cells.selectAll("g").data(data);

        // add cell group and interactivity
        this.cells_enter = this.cells_data
            .enter()
            .append("g")
            .attr("class", "exp_heatmap_cell")
            .on("click", function(d) {
                d3.selectAll(".exp_heatmap_cell_block")
                    .style("stroke", "none")
                    .style("stroke-width", 2);
                d3.select(this)
                    .select("rect")
                    .style("stroke", "black")
                    .style("stroke-width", 2);

                self.store.setTableDataFilters(d);
            });
        this.bind_tooltip(this.cells_enter, "cell");

        // add cell fill
        this.cells_enter
            .append("rect")
            .attr("class", "exp_heatmap_cell_block")
            .attr("x", d => this.x_scale(d.x_step))
            .attr("y", d => this.y_scale(d.y_step))
            .attr("width", this.x_scale.rangeBand())
            .attr("height", this.y_scale.rangeBand());

        /// add cell text
        this.cells_enter
            .append("text")
            .attr("class", "exp_heatmap_cell_text")
            .attr("x", d => this.x_scale(d.x_step) + this.x_scale.rangeBand() / 2)
            .attr("y", d => this.y_scale(d.y_step) + this.y_scale.rangeBand() / 2);

        // enter/update
        this.cells_data
            .select(".exp_heatmap_cell_block")
            .transition()
            .style("fill", d => this.color_scale(d.rows.length));

        this.cells_data
            .select(".exp_heatmap_cell_text")
            .transition()
            .style("fill", d => {
                let {r, g, b} = d3.rgb(this.color_scale(d.rows.length));
                ({r, g, b} = h.getTextContrastColor(r, g, b));
                return d3.rgb(r, g, b);
            })
            .style("display", d => (d.rows.length == 0 ? "none" : null))
            .text(d => d.rows.length);

        this.cells_data.exit().remove();
    };

    build_plot() {
        // Clear plot div and and append new svg object
        this.plot_div.empty();
        this.vis = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("class", "d3")
            .attr("preserveAspectRatio", "xMinYMin")
            .append("g");
        this.svg = this.vis[0][0].parentNode;

        // Scales for x axis and y axis
        this.x_scale = d3.scale
            .ordinal()
            .domain(_.range(0, this.x_steps))
            .rangeBands([0, this.w]);
        this.y_scale = d3.scale
            .ordinal()
            .domain(_.range(0, this.y_steps))
            .rangeBands([0, this.h]);

        // Draw cells
        this.cells = this.vis.append("g");

        autorun(() => this.update_plot(this.store.matrixDataset));

        // Draw axes
        this.build_axes();

        // Draw labels
        this.build_labels();

        // Set plot dimensions and viewbox
        let w = this.w + this.settings.padding.left + this.settings.padding.right,
            h = this.h + this.settings.padding.top + this.settings.padding.bottom;
        d3.select(this.svg)
            .attr("width", w)
            .attr("height", h)
            .attr("viewBox", `0 0 ${w} ${h}`);

        // Position plot
        this.vis.attr(
            "transform",
            `translate(${this.settings.padding.left},${this.settings.padding.top})`
        );
    }
}

export default ExploreHeatmapPlot;
