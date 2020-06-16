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
import Tooltip from "./heatmap/Tooltip";

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

        if (hasFilters) {
            ReactDOM.render(<FilterWidgetContainer store={this.store} />, filters);
        }
    }

    set_trigger_resize() {
        var self = this,
            w =
                this.w +
                this.settings.padding.left +
                this.x_axis_label_padding +
                this.settings.padding.right,
            h =
                this.h +
                this.settings.padding.top +
                this.y_axis_label_padding +
                this.settings.padding.bottom,
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

        const {compress_x, compress_y} = this.settings,
            {scales, totals} = this.store;
        this.x_steps = scales.x.filter((d, i) => (compress_x ? totals.x[i] > 0 : true)).length;
        this.y_steps = scales.y.filter((d, i) => (compress_y ? totals.y[i] > 0 : true)).length;

        this.w = this.settings.cell_width * this.x_steps;
        this.h = this.settings.cell_height * this.y_steps;

        // calculated padding based on labels
        this.x_axis_label_padding = 0;
        this.y_axis_label_padding = 0;
    }

    bind_tooltip(selection, type) {
        if (!this.settings.show_tooltip) {
            return;
        }

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

    get_matching_cells(filters, axis) {
        let property;
        if (axis == "x") property = "x_filters";
        else if (axis == "y") property = "y_filters";

        return this.store.matrixDataset.filter(d => {
            for (const filter of filters) {
                let included = false;
                for (const cell_filter of d[property]) {
                    if (_.isMatch(cell_filter, filter) && d.rows.length > 0) included = true;
                }
                if (!included) return false;
            }
            return true;
        });
    }

    build_axes() {
        let xs = this.store.scales.x.filter((d, i) =>
                this.store.settings.compress_x ? this.store.totals.x[i] > 0 : true
            ),
            ys = this.store.scales.y.filter((d, i) =>
                this.store.settings.compress_y ? this.store.totals.y[i] > 0 : true
            ),
            xAxis = this.vis
                .append("g")
                .attr("class", ".xAxis")
                .attr("transform", `translate(0,${this.h})`),
            yAxis = this.vis.append("g").attr("class", ".yAxis"),
            thisItem,
            label_padding = 6;

        // build x-axis
        let yOffset = 0,
            numXAxes = xs.length == 0 ? 0 : xs[0].length,
            {cell_width, show_axis_border} = this.store.settings;
        for (let i = numXAxes - 1; i >= 0; i--) {
            let axis = xAxis.append("g").attr("transform", `translate(0,${yOffset})`),
                lastItem = xs[0],
                itemStartIndex = 0,
                numItems = 0,
                borderData = [];

            for (let j = 0; j <= xs.length; j++) {
                thisItem = j < xs.length ? xs[j] : null;
                if (
                    thisItem == null ||
                    !_.isMatch(thisItem[i], lastItem[i]) ||
                    (i > 0 && !_.isMatch(thisItem[i - 1], lastItem[i - 1]))
                ) {
                    let label = axis.append("g");

                    label
                        .append("text")
                        .attr("transform", `rotate(${this.settings.x_tick_rotate})`)
                        .text(lastItem[i].value);

                    let box = label.node().getBBox(),
                        label_offset =
                            itemStartIndex * cell_width +
                            (numItems * cell_width) / 2 -
                            box.width / 2;

                    label.attr(
                        "transform",
                        `translate(${label_offset - box.x},${label_padding - box.y})`
                    );

                    borderData.push({
                        filters: _.slice(lastItem, 0, i + 1),
                        x1: itemStartIndex * cell_width,
                        width: numItems * cell_width,
                    });

                    itemStartIndex = j;
                    numItems = 0;
                }
                numItems += 1;
                lastItem = thisItem;
            }

            let box = axis.node().getBBox();

            let newYOffset = yOffset + box.height + label_padding * 2;
            let border = xAxis
                .selectAll(".none")
                .data(borderData)
                .enter()
                .append("polyline")
                .attr(
                    "points",
                    d =>
                        `${d.x1},${newYOffset} ${d.x1},${yOffset} ${d.x1 +
                            d.width},${yOffset} ${d.x1 + d.width},${newYOffset}`
                )
                .attr("fill", "transparent")
                .attr("stroke", show_axis_border ? "black" : null)
                .on("click", d => {
                    const cells = this.get_matching_cells(d.filters, "x");
                    this.store.setTableDataFilters(new Set(cells));
                });
            this.bind_tooltip(border, "axis");
            yOffset = newYOffset;
        }

        // build y-axis
        let xOffset = 0,
            numYAxes = ys.length == 0 ? 0 : ys[0].length,
            {cell_height} = this.store.settings;
        for (let i = numYAxes - 1; i >= 0; i--) {
            let axis = yAxis.append("g").attr("transform", `translate(${-xOffset},0)`),
                lastItem = ys[0],
                itemStartIndex = 0,
                numItems = 0,
                borderData = [];
            for (let j = 0; j <= ys.length; j++) {
                thisItem = j < ys.length ? ys[j] : null;
                if (
                    thisItem == null ||
                    !_.isMatch(thisItem[i], lastItem[i]) ||
                    (i > 0 && !_.isMatch(thisItem[i - 1], lastItem[i - 1]))
                ) {
                    let label = axis.append("g");
                    label
                        .append("text")
                        .attr("transform", `rotate(${this.settings.y_tick_rotate})`)
                        .text(lastItem[i].value);
                    let box = label.node().getBBox(),
                        label_offset =
                            itemStartIndex * cell_height +
                            (numItems * cell_height) / 2 -
                            box.height / 2;
                    label.attr(
                        "transform",
                        `translate(${-box.width - box.x - label_padding},${label_offset - box.y})`
                    );

                    borderData.push({
                        filters: _.slice(lastItem, 0, i + 1),
                        y1: itemStartIndex * cell_height,
                        height: numItems * cell_height,
                    });

                    itemStartIndex = j;
                    numItems = 0;
                }
                numItems += 1;
                lastItem = thisItem;
            }

            let box = axis.node().getBBox(),
                newXOffset = xOffset + box.width + label_padding * 2;
            let border = yAxis
                .selectAll(".none")
                .data(borderData)
                .enter()
                .append("polyline")
                .attr(
                    "points",
                    d =>
                        `${-newXOffset},${d.y1} ${-xOffset},${d.y1} ${-xOffset},${d.y1 +
                            d.height} ${-newXOffset},${d.y1 + d.height}`
                )
                .attr("fill", "transparent")
                .attr("stroke", show_axis_border ? "black" : null)
                .on("click", d => {
                    const cells = this.get_matching_cells(d.filters, "y");
                    this.store.setTableDataFilters(new Set(cells));
                });
            this.bind_tooltip(border, "axis");
            xOffset = newXOffset;
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
            x_band = this.x_steps == 0 ? 0 : this.w / this.x_steps,
            y_band = this.y_steps == 0 ? 0 : this.h / this.y_steps;

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
            {tableDataFilters, maxValue, colorScale} = this.store;

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
                if (d.rows.length > 0) {
                    d3.select(this)
                        .select("rect")
                        .style("stroke", "black")
                        .style("stroke-width", 2);

                    self.store.setTableDataFilters(d);
                } else {
                    self.store.setTableDataFilters(new Set());
                }
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
            .style("fill", d => {
                const filterIndices = [...tableDataFilters].map(e => e.index),
                    value =
                        tableDataFilters.size == 0
                            ? d.rows.length
                            : _.includes(filterIndices, d.index)
                            ? maxValue
                            : d.rows.length / 3;
                return colorScale(value);
            });

        this.cells_data
            .select(".exp_heatmap_cell_text")
            .transition()
            .style("fill", d => {
                const filterIndices = [...tableDataFilters].map(e => e.index),
                    value =
                        tableDataFilters.size == 0
                            ? d.rows.length
                            : _.includes(filterIndices, d.index)
                            ? maxValue
                            : d.rows.length / 3;
                return h.getTextContrastColor(colorScale(value));
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
