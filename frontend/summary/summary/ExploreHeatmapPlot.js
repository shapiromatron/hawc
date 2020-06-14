import _ from "lodash";
import d3 from "d3";
import {autorun} from "mobx";
import D3Visualization from "./D3Visualization";
import h from "shared/utils/helpers";
import HAWCModal from "utils/HAWCModal";
import HAWCUtils from "utils/HAWCUtils";

import React from "react";
import ReactDOM from "react-dom";
import HeatmapDatastore from "./heatmap/HeatmapDatastore";
import DatasetTable from "./heatmap/DatasetTable";
import FilterWidgetContainer from "./heatmap/FilterWidgetContainer";

class ExploreHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        super(...arguments);
        this.modal = new HAWCModal();
        this.store = new HeatmapDatastore(data.settings, data.dataset);
        this.dataset = data.dataset;
        this.settings = data.settings;
        this.options = options || {};
        this.generate_properties();
    }

    render($div) {
        const hasFilters = this.settings.filter_widgets.length > 0,
            text1 = hasFilters
                ? `<div class="span9 heatmap-viz"></div><div class="span3 heatmap-filters"></div>`
                : `<div class="span12 heatmap-viz"></div>`;

        // Create svg container
        $div.html(`<div class="row-fluid">
            ${text1}
            <div class="${hasFilters ? "span9" : "span12"} heatmap-tables"></div>
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
        if (hasFilters) {
            ReactDOM.render(<FilterWidgetContainer store={this.store} />, filters);
        }
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

        // calculated padding based on labels
        this.x_axis_label_padding = 0;
        this.y_axis_label_padding = 0;
    }

    build_axes() {
        let generate_ticks = domain => {
                if (domain.length == 0) return [];
                let ticks = [];

                ticks.push(domain[0]);
                for (let i = 1; i < domain.length; i++) {
                    let current_ticks = [];
                    for (let j = 0; j < ticks[i - 1].length; j++) {
                        current_ticks = current_ticks.concat(domain[i]);
                    }
                    ticks.push(current_ticks);
                }
                return ticks;
            },
            x_domains = generate_ticks(this.x_domain).reverse(),
            y_domains = generate_ticks(this.y_domain).reverse(),
            x_axis_offset = 0,
            y_axis_offset = 0,
            label_padding = 6;

        /// Build x axes
        // For each axis...
        let xAxis = this.vis.append("g").attr("class", ".xAxis");
        for (let i = 0; i < x_domains.length; i++) {
            let axis = xAxis
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
                    .attr("transform", `rotate(${this.settings.x_tick_rotate})`)
                    .text(domain[j]);
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
            x_axis_offset += max;

            // Adds a border around tick labels
            let add_border = () => {
                let borders = axis.append("g");
                for (let j = 0; j < domain.length; j++) {
                    borders
                        .append("polyline")
                        .attr(
                            "points",
                            `${band * j},${max} ${band * j},0 ${band * (j + 1)},0 ${band *
                                (j + 1)},${max}`
                        )
                        .attr("fill", "none")
                        .attr("stroke", "black");
                }
            };
            if (this.settings.show_axis_border) {
                add_border();
            }
        }

        /// Build y axes
        // For each axis...
        let yAxis = this.vis.append("g").attr("class", ".yAxis");
        for (let i = 0; i < y_domains.length; i++) {
            let axis = yAxis.append("g").attr("transform", `translate(${-y_axis_offset},0)`),
                domain = y_domains[i],
                band = this.h / domain.length,
                mid = band / 2,
                max = 0;
            // For each tick...
            for (let j = 0; j < domain.length; j++) {
                let label = axis.append("g");
                label
                    .append("text")
                    .attr("transform", `rotate(${this.settings.y_tick_rotate})`)
                    .text(domain[j]);
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
            y_axis_offset += max;

            // Adds a border around tick labels
            let add_border = () => {
                let borders = axis.append("g");
                for (let j = 0; j < domain.length; j++) {
                    borders
                        .append("polyline")
                        .attr(
                            "points",
                            `${-max},${band * j} 0,${band * j} 0,${band * (j + 1)} ${-max},${band *
                                (j + 1)}`
                        )
                        .attr("fill", "none")
                        .attr("stroke", "black");
                }
            };
            if (this.settings.show_axis_border) {
                add_border();
            }
        }
        this.x_axis_label_padding = yAxis.node().getBoundingClientRect().width;
        this.y_axis_label_padding = xAxis.node().getBoundingClientRect().height;
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
        let label_margin = 20,
            isDev = this.options.dev;

        // Plot title
        if (this.settings.title.text.length > 0) {
            let titleSettings = this.settings.title,
                x =
                    titleSettings.x === 0
                        ? this.padding.left + this.x_axis_label_padding + this.w / 2
                        : titleSettings.x,
                y = titleSettings.y === 0 ? label_margin : titleSettings.y,
                title = d3
                    .select(this.svg)
                    .append("text")
                    .attr("class", "exp_heatmap_title exp_heatmap_label")
                    .attr("transform", `translate(${x},${y}) rotate(${titleSettings.rotate})`)
                    .text(titleSettings.text);

            if (isDev) {
                title.attr("cursor", "pointer").call(
                    HAWCUtils.updateDragLocationTransform((x, y) => {
                        this.settings.title.x = parseInt(x);
                        this.settings.title.y = parseInt(y);
                    })
                );
            }
        }

        // X axis
        if (this.settings.x_label.text.length > 0) {
            let xLabelSettings = this.settings.x_label,
                x =
                    xLabelSettings.x === 0
                        ? this.padding.left + this.x_axis_label_padding + this.w / 2
                        : xLabelSettings.x,
                y =
                    xLabelSettings.y === 0
                        ? this.padding.top + this.h + this.y_axis_label_padding + label_margin
                        : xLabelSettings.y,
                xLabel = d3
                    .select(this.svg)
                    .append("text")
                    .attr("class", "exp_heatmap_label")
                    .attr("transform", `translate(${x},${y}) rotate(${xLabelSettings.rotate})`)
                    .text(xLabelSettings.text);

            if (isDev) {
                xLabel.attr("cursor", "pointer").call(
                    HAWCUtils.updateDragLocationTransform((x, y) => {
                        this.settings.x_label.x = parseInt(x);
                        this.settings.x_label.y = parseInt(y);
                    })
                );
            }
        }

        // Y axis
        if (this.settings.y_label.text.length > 0) {
            let yLabelSettings = this.settings.y_label,
                x =
                    yLabelSettings.x === 0
                        ? this.settings.padding.left - label_margin / 2
                        : yLabelSettings.x,
                y =
                    yLabelSettings.y === 0
                        ? this.settings.padding.top + this.h / 2
                        : yLabelSettings.y,
                yLabel = d3
                    .select(this.svg)
                    .append("text")
                    .attr("class", "exp_heatmap_label")
                    .attr("transform", `translate(${x},${y}) rotate(${yLabelSettings.rotate})`)
                    .text(yLabelSettings.text);

            if (isDev) {
                yLabel.attr("cursor", "pointer").call(
                    HAWCUtils.updateDragLocationTransform((x, y) => {
                        this.settings.y_label.x = parseInt(x);
                        this.settings.y_label.y = parseInt(y);
                    })
                );
            }
        }
    }

    update_plot = data => {
        const self = this,
            cells_data = this.cells.selectAll("g").data(data),
            {tableDataFilters, maxValue, colorScale} = this.store;

        // add cell group and interactivity
        this.cells_enter = cells_data
            .enter()
            .append("g")
            .attr("class", "exp_heatmap_cell")
            .on("click", function(d) {
                d3.selectAll(".exp_heatmap_cell_block")
                    .style("stroke", "none")
                    .style("stroke-width", 2);

                if (d.rows.length > 0) {
                    d3.select(this)
                        .select("rect")
                        .style("stroke", "black")
                        .style("stroke-width", 2);

                    self.store.updateTableDataFilters(d);
                } else {
                    self.store.updateTableDataFilters(null);
                }
            })
            .on("mouseover", null);

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
        cells_data
            .select(".exp_heatmap_cell_block")
            .transition()
            .style("fill", d => {
                const value =
                    tableDataFilters == null
                        ? d.rows.length
                        : tableDataFilters.index === d.index
                        ? maxValue
                        : d.rows.length / 3;
                return colorScale(value);
            });

        cells_data
            .select(".exp_heatmap_cell_text")
            .transition()
            .style("fill", d => {
                const value =
                    tableDataFilters == null
                        ? d.rows.length
                        : tableDataFilters.index === d.index
                        ? maxValue
                        : d.rows.length / 3;
                return h.getTextContrastColor(colorScale(value));
            })
            .style("display", d => (d.rows.length == 0 ? "none" : null))
            .text(d => d.rows.length);

        cells_data.exit().remove();
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

        // Set plot dimensions and viewBox
        let w =
                this.settings.padding.left +
                this.x_axis_label_padding +
                this.w +
                this.settings.padding.right,
            h =
                this.settings.padding.top +
                this.h +
                this.y_axis_label_padding +
                this.settings.padding.bottom;

        d3.select(this.svg)
            .attr("width", w)
            .attr("height", h)
            .attr("viewBox", `0 0 ${w} ${h}`);

        // Position plot
        this.vis.attr(
            "transform",
            `translate(${this.settings.padding.left + this.x_axis_label_padding},${
                this.settings.padding.top
            })`
        );
    }
}

export default ExploreHeatmapPlot;
