import * as d3 from "d3";
import _ from "lodash";
import {autorun} from "mobx";
import React from "react";
import ReactDOM from "react-dom";
import bindTooltip from "shared/components/Tooltip";
import VisualToolbar from "shared/components/VisualToolbar";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";
import h from "shared/utils/helpers";

import {AxisTooltip, CellTooltip} from "./heatmap/Tooltip";

const AXIS_WIDTH_GUESS = 120,
    AUTOROTATE_TEXT_WRAP_X = 100,
    AUTOROTATE_TEXT_WRAP_Y = 200;

class ExploreHeatmapPlot {
    constructor(store, options) {
        this.modal = new HAWCModal();
        this.store = store;
        this.options = options;
    }

    render(div, tooltipDiv) {
        this.plot_div = $(div);
        this.$tooltipDiv = $(tooltipDiv);
        this.generate_properties();
        this.build_plot();
    }

    generate_properties() {
        const {settings, scales, totals} = this.store;

        // `this.padding` required for D3Plot
        this.padding = settings.padding;

        this.xs = this.store.scales.x.filter((_d, i) =>
            settings.compress_x ? this.store.totals.x[i] > 0 : true
        );
        this.ys = this.store.scales.y.filter((_d, i) =>
            settings.compress_y ? this.store.totals.y[i] > 0 : true
        );

        this.x_steps = scales.x.filter((_d, i) =>
            settings.compress_x ? totals.x[i] > 0 : true
        ).length;
        this.y_steps = scales.y.filter((_d, i) =>
            settings.compress_y ? totals.y[i] > 0 : true
        ).length;

        this.x_steps = settings.show_totals ? this.x_steps + 1 : this.x_steps;
        this.y_steps = settings.show_totals ? this.y_steps + 1 : this.y_steps;

        // calculated padding based on labels
        this.x_axis_label_padding = 0;
        this.y_axis_label_padding = 0;
    }

    get_cell_dimensions() {
        const {settings} = this.store;
        let cellDimensions = {};
        if (settings.autosize_cells) {
            /*
            Assume plot has the the same width/height ratio as browser window.

            Calculate total plotHeight and plotWidth but getting available room, and then subtracting
            padding. In addition, subtract AXIS_WIDTH_GUESS for each axis.  This could be improved
            in the future by laying-out the largest text label by text-size and getting the size.
            */

            // minimum dimensions
            const minWidth = 50,
                minHeight = 25;

            // dimensions from labels
            const xRotate = settings.autorotate_tick_labels ? -90 : settings.x_tick_rotate,
                yRotate = settings.autorotate_tick_labels ? 0 : settings.y_tick_rotate,
                xLabelDimensions = this.get_max_tick_dimensions(
                    this.xs,
                    settings.x_fields,
                    AUTOROTATE_TEXT_WRAP_X,
                    xRotate
                ),
                yLabelDimensions = this.get_max_tick_dimensions(
                    this.ys,
                    settings.y_fields,
                    AUTOROTATE_TEXT_WRAP_Y,
                    yRotate
                ),
                labelWidth = xLabelDimensions.width,
                labelHeight = yLabelDimensions.height;

            // dimensions from plot
            const plotWidth =
                    this.plot_div.width() -
                    settings.padding.left -
                    settings.padding.right -
                    settings.y_fields.length * AXIS_WIDTH_GUESS,
                plotHeight =
                    (plotWidth / $(window).width()) * $(window).height() -
                    settings.padding.top -
                    settings.padding.bottom -
                    settings.x_fields.length * AXIS_WIDTH_GUESS,
                cellWidth = this.x_steps == 0 ? 0 : plotWidth / this.x_steps,
                cellHeight = this.y_steps == 0 ? 0 : plotHeight / this.y_steps;

            cellDimensions = {
                width: Math.max(cellWidth, labelWidth, minWidth),
                height: Math.max(cellHeight, labelHeight, minHeight),
            };
        } else {
            cellDimensions = {width: settings.cell_width, height: settings.cell_height};
        }
        return cellDimensions;
    }

    bind_tooltip(selection, type) {
        if (!this.store.settings.show_tooltip) {
            return;
        }

        if (type === "cell") {
            bindTooltip(this.$tooltipDiv, selection, (_event, d) => (
                <CellTooltip data={d} count={this.store.getCount(d.rows)} />
            ));
        } else if (type === "axis") {
            bindTooltip(this.$tooltipDiv, selection, (_event, d) => <AxisTooltip data={d} />);
        } else {
            throw `Unknown type: ${type}`;
        }
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

    get_max_tick_dimensions(scale, fields, default_wrap, rotate) {
        let tempGroup = this.vis.append("g"),
            tempText = tempGroup.append("text"),
            maxWidth = 0,
            maxHeight = 0;
        _.each(scale, column =>
            _.each(column, (filter, index) => {
                let wrap_text = fields[index].wrap_text ? fields[index].wrap_text : default_wrap;
                tempText
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("transform", `rotate(${rotate ? rotate : 0})`)
                    .html("")
                    .text(filter.value);
                if (wrap_text) {
                    HAWCUtils.wrapText(tempText.node(), wrap_text);
                }
                const box = tempGroup.node().getBBox();
                maxWidth = Math.max(box.width, maxWidth);
                maxHeight = Math.max(box.height, maxHeight);
            })
        );
        tempGroup.remove();
        return {width: maxWidth, height: maxHeight};
    }

    build_x_axis() {
        const {settings} = this.store;

        let xAxis = this.vis.append("g").attr("class", "xAxis exp-heatmap-axis"),
            thisItem,
            label_padding = 6,
            {x_tick_rotate, autorotate_tick_labels} = settings;

        if (settings.x_axis_bottom) {
            xAxis.attr("transform", `translate(0,${this.h})`);
        }

        if (autorotate_tick_labels) {
            const xMax = this.get_max_tick_dimensions(
                    this.xs,
                    settings.x_fields,
                    AUTOROTATE_TEXT_WRAP_X
                ),
                {width} = this.cellDimensions;
            x_tick_rotate =
                width > xMax.width
                    ? 0
                    : width > xMax.height
                      ? -90
                      : xMax.width < xMax.height
                        ? 0
                        : -90;
        }

        x_tick_rotate = ((x_tick_rotate % 360) + 360) % 360; // make rotation between 0 and 360

        // build x-axis
        let yOffset = 0,
            numXAxes = this.xs.length == 0 ? 0 : this.xs[0].length,
            {show_axis_border} = settings,
            textAnchor = settings.x_axis_bottom
                ? x_tick_rotate >= 0 && x_tick_rotate <= 180
                    ? "start"
                    : "end"
                : x_tick_rotate > 0 && x_tick_rotate < 180
                  ? "end"
                  : "start";
        for (let i = numXAxes - 1; i >= 0; i--) {
            let axis = xAxis
                    .append("g")
                    .attr(
                        "transform",
                        `translate(0,${
                            yOffset + (settings.x_axis_bottom ? label_padding : -label_padding)
                        })`
                    )
                    .attr("text-anchor", textAnchor),
                lastItem = this.xs[0],
                itemStartIndex = 0,
                numItems = 0,
                borderData = [],
                wrap_text = settings.x_fields[i].wrap_text
                    ? settings.x_fields[i].wrap_text
                    : AUTOROTATE_TEXT_WRAP_X;

            for (let j = 0; j <= this.xs.length; j++) {
                thisItem = j < this.xs.length ? this.xs[j] : null;
                if (
                    thisItem == null ||
                    !_.isMatch(thisItem[i], lastItem[i]) ||
                    (i > 0 && !_.isMatch(thisItem[i - 1], lastItem[i - 1]))
                ) {
                    let label = axis.append("g");

                    label
                        .append("text")
                        .attr("x", 0)
                        .attr("y", 0)
                        .attr("transform", `rotate(${x_tick_rotate})`)
                        .text(lastItem[i].value || h.nullString)
                        .each(function () {
                            if (wrap_text) {
                                HAWCUtils.wrapText(this, wrap_text);
                            }
                        });

                    let box = label.node().getBBox(),
                        label_x_offset =
                            itemStartIndex * this.cellDimensions.width +
                            (numItems * this.cellDimensions.width) / 2 -
                            box.width / 2,
                        label_y_offset = settings.x_axis_bottom ? 0 : -box.height;

                    label.attr(
                        "transform",
                        `translate(${-box.x + label_x_offset},${-box.y + label_y_offset})`
                    );

                    borderData.push({
                        filters: _.slice(lastItem, 0, i + 1),
                        x1: itemStartIndex * this.cellDimensions.width,
                        width: numItems * this.cellDimensions.width,
                    });

                    itemStartIndex = j;
                    numItems = 0;
                }
                numItems += 1;
                lastItem = thisItem;
            }
            if (settings.show_totals && i == numXAxes - 1) {
                let label = axis.append("g");
                label
                    .append("text")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("transform", `rotate(${x_tick_rotate})`)
                    .text("Grand Total")
                    .style("font-weight", "bold");

                let box = label.node().getBBox(),
                    label_x_offset =
                        this.xs.length * this.cellDimensions.width +
                        this.cellDimensions.width / 2 -
                        box.width / 2,
                    label_y_offset = settings.x_axis_bottom ? 0 : -box.height;

                label.attr(
                    "transform",
                    `translate(${-box.x + label_x_offset},${-box.y + label_y_offset})`
                );
            }

            let box = axis.node().getBBox();

            let yOffsetDiff = settings.x_axis_bottom
                    ? box.height + label_padding * 2
                    : -(box.height + label_padding * 2),
                newYOffset = yOffset + yOffsetDiff;
            let border = xAxis
                .append("g")
                .attr("fill-opacity", 0)
                .attr("stroke", show_axis_border ? "black" : null)
                .selectAll(".none")
                .data(borderData)
                .enter()
                .append("polyline")
                .attr(
                    "points",
                    d =>
                        `${d.x1},${newYOffset} ${d.x1},${yOffset} ${
                            d.x1 + d.width
                        },${yOffset} ${d.x1 + d.width},${newYOffset}`
                )
                .on("click", (_event, d) => {
                    const cells = this.get_matching_cells(d.filters, "x");
                    this.store.setTableDataFilters(new Set(cells));
                });
            this.bind_tooltip(border, "axis");
            yOffset = newYOffset;
        }

        if (settings.show_totals) {
            const x1 = this.xs.length * this.cellDimensions.width,
                x2 = x1 + this.cellDimensions.width,
                y1 = settings.x_axis_bottom
                    ? xAxis.node().getBBox().height
                    : -xAxis.node().getBBox().height,
                y2 = 0;
            xAxis
                .append("polyline")
                .attr("points", _d => `${x1},${y1} ${x1},${y2} ${x2},${y2} ${x2},${y1}`)
                .attr("fill-opacity", 0)
                .attr("stroke", show_axis_border ? "black" : null);
        }

        this.y_axis_label_padding = xAxis.node().getBoundingClientRect().height;
    }

    build_y_axis() {
        const {settings} = this.store;

        let yAxis = this.vis.append("g").attr("class", "yAxis exp-heatmap-axis"),
            thisItem,
            label_padding = 6,
            {y_tick_rotate, autorotate_tick_labels} = settings;

        if (autorotate_tick_labels) {
            y_tick_rotate = 0;
        }

        y_tick_rotate = ((y_tick_rotate % 360) + 360) % 360; // make rotation between 0 and 360

        // build y-axis
        let xOffset = 0,
            numYAxes = this.ys.length == 0 ? 0 : this.ys[0].length,
            {show_axis_border} = settings,
            textAnchor = y_tick_rotate >= 90 && y_tick_rotate <= 270 ? "start" : "end";
        for (let i = numYAxes - 1; i >= 0; i--) {
            let axis = yAxis
                    .append("g")
                    .attr("transform", `translate(${-xOffset - label_padding},0)`)
                    .attr("text-anchor", textAnchor),
                lastItem = this.ys[0],
                itemStartIndex = 0,
                numItems = 0,
                borderData = [],
                wrap_text = settings.y_fields[i].wrap_text
                    ? settings.y_fields[i].wrap_text
                    : AUTOROTATE_TEXT_WRAP_Y;

            for (let j = 0; j <= this.ys.length; j++) {
                thisItem = j < this.ys.length ? this.ys[j] : null;
                if (
                    thisItem == null ||
                    !_.isMatch(thisItem[i], lastItem[i]) ||
                    (i > 0 && !_.isMatch(thisItem[i - 1], lastItem[i - 1]))
                ) {
                    let label = axis.append("g");
                    label
                        .append("text")
                        .attr("x", 0)
                        .attr("y", 0)
                        .attr("transform", `rotate(${y_tick_rotate})`)
                        .text(lastItem[i].value || h.nullString)
                        .each(function () {
                            if (wrap_text) {
                                HAWCUtils.wrapText(this, wrap_text);
                            }
                        });
                    let box = label.node().getBBox(),
                        label_x_offset = -box.width,
                        label_y_offset =
                            itemStartIndex * this.cellDimensions.height +
                            (numItems * this.cellDimensions.height) / 2 -
                            box.height / 2;
                    label.attr(
                        "transform",
                        `translate(${-box.x + label_x_offset},${-box.y + label_y_offset})`
                    );

                    borderData.push({
                        filters: _.slice(lastItem, 0, i + 1),
                        y1: itemStartIndex * this.cellDimensions.height,
                        height: numItems * this.cellDimensions.height,
                    });

                    itemStartIndex = j;
                    numItems = 0;
                }
                numItems += 1;
                lastItem = thisItem;
            }
            if (settings.show_totals && i == numYAxes - 1) {
                let label = axis.append("g");
                label
                    .append("text")
                    .attr("x", 0)
                    .attr("y", 0)
                    .attr("transform", `rotate(${y_tick_rotate})`)
                    .text("Grand Total")
                    .style("font-weight", "bold");

                let box = label.node().getBBox(),
                    label_y_offset =
                        this.ys.length * this.cellDimensions.height +
                        this.cellDimensions.height / 2 -
                        box.height / 2;

                label.attr(
                    "transform",
                    `translate(${-box.x - box.width},${-box.y + label_y_offset})`
                );
            }

            let box = axis.node().getBBox(),
                width = box.width + label_padding * 2;
            let border = yAxis
                .append("g")
                .attr("transform", `translate(${-xOffset},0)`)
                .attr("fill-opacity", 0)
                .attr("stroke", show_axis_border ? "black" : null)
                .selectAll(".none")
                .data(borderData)
                .enter()
                .append("polyline")
                .attr(
                    "points",
                    d =>
                        `${-width},${d.y1} 0,${d.y1} 0,${d.y1 + d.height} ${-width},${
                            d.y1 + d.height
                        }`
                )
                .on("click", (_event, d) => {
                    const cells = this.get_matching_cells(d.filters, "y");
                    this.store.setTableDataFilters(new Set(cells));
                });
            this.bind_tooltip(border, "axis");
            xOffset = xOffset + width;
        }
        if (settings.show_totals) {
            const x1 = -yAxis.node().getBBox().width,
                x2 = 0,
                y1 = this.ys.length * this.cellDimensions.height,
                y2 = y1 + this.cellDimensions.height;
            yAxis
                .append("polyline")
                .attr("points", _d => `${x1},${y1} ${x2},${y1} ${x2},${y2} ${x1},${y2}`)
                .attr("fill-opacity", 0)
                .attr("stroke", show_axis_border ? "black" : null);
        }

        this.x_axis_label_padding = yAxis.node().getBoundingClientRect().width;
    }

    build_axes() {
        this.build_y_axis();
        this.build_x_axis();
    }

    add_grid() {
        if (!this.store.settings.show_grid) {
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
        const {settings} = this.store;
        let label_margin = 20,
            isDev = this.options.dev;

        // Plot title
        if (settings.title.text.length > 0) {
            let titleSettings = settings.title,
                x =
                    titleSettings.x === 0
                        ? this.padding.left + this.x_axis_label_padding + this.w / 2
                        : titleSettings.x,
                y =
                    titleSettings.y === 0
                        ? (settings.x_axis_bottom ? 0 : -this.y_axis_label_padding) + label_margin
                        : titleSettings.y,
                title = d3
                    .select(this.svg)
                    .append("text")
                    .attr("class", "exp_heatmap_title exp_heatmap_label")
                    .attr("transform", `translate(${x},${y}) rotate(${titleSettings.rotate})`)
                    .text(titleSettings.text);

            if (isDev) {
                title.attr("cursor", "pointer").call(
                    HAWCUtils.updateDragLocationTransform((x, y) => {
                        settings.title.x = parseInt(x);
                        settings.title.y = parseInt(y);
                    })
                );
            }
        }

        // X axis
        if (settings.x_label.text.length > 0) {
            let xLabelSettings = settings.x_label,
                x =
                    xLabelSettings.x === 0
                        ? this.padding.left + this.x_axis_label_padding + this.w / 2
                        : xLabelSettings.x,
                y =
                    xLabelSettings.y === 0
                        ? this.padding.top +
                          this.h +
                          (settings.x_axis_bottom ? this.y_axis_label_padding : 0) +
                          label_margin
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
                        settings.x_label.x = parseInt(x);
                        settings.x_label.y = parseInt(y);
                    })
                );
            }
        }

        // Y axis
        if (settings.y_label.text.length > 0) {
            let yLabelSettings = settings.y_label,
                x =
                    yLabelSettings.x === 0
                        ? settings.padding.left - label_margin / 2
                        : yLabelSettings.x,
                y = yLabelSettings.y === 0 ? settings.padding.top + this.h / 2 : yLabelSettings.y,
                yLabel = d3
                    .select(this.svg)
                    .append("text")
                    .attr("class", "exp_heatmap_label")
                    .attr("transform", `translate(${x},${y}) rotate(${yLabelSettings.rotate})`)
                    .text(yLabelSettings.text);

            if (isDev) {
                yLabel.attr("cursor", "pointer").call(
                    HAWCUtils.updateDragLocationTransform((x, y) => {
                        settings.y_label.x = parseInt(x);
                        settings.y_label.y = parseInt(y);
                    })
                );
            }
        }
    }

    update_plot = data => {
        const self = this,
            {tableDataFilters, maxValue, colorScale, settings} = this.store,
            showCounts = settings.show_counts,
            cellColor = d => {
                const filterIndices = [...tableDataFilters].map(e => e.index),
                    count = this.store.getCount(d.rows),
                    value =
                        tableDataFilters.size == 0
                            ? count
                            : _.includes(filterIndices, d.index)
                              ? maxValue
                              : count / 3;
                return showCounts <= 2
                    ? colorScale(value)
                    : value === 0
                      ? "white"
                      : colorScale(maxValue / 3);
            },
            totalColor = d => {
                const filterIndices = [...tableDataFilters].map(e => e.index);
                return _.includes(filterIndices, d.index) ? colorScale(maxValue) : "#eeeeee";
            },
            textColor = d => {
                const backgroundColor = d.type == "cell" ? cellColor(d) : totalColor(d);
                return h.getTextContrastColor(backgroundColor);
            };

        this.vis
            .select(".exp_heatmap_cells")
            .selectAll(".exp_heatmap_cell")
            .data(data, d => d.index)
            .join(
                enter => {
                    let g = enter
                        .append("g")
                        .attr("class", "exp_heatmap_cell")
                        .on("click", (_event, d) => {
                            if (d.rows.length > 0) {
                                self.store.setTableDataFilters(d);
                            } else {
                                self.store.setTableDataFilters(new Set());
                            }
                        });

                    g.append("rect")
                        .attr("x", d => this.x_scale(d.x_step))
                        .attr("y", d => this.y_scale(d.y_step))
                        .attr("width", this.x_scale.bandwidth())
                        .attr("height", this.y_scale.bandwidth())
                        .attr("fill", "white");

                    g.append("text")
                        .attr("class", "exp_heatmap_cell_text")
                        .attr("x", d => this.x_scale(d.x_step) + this.x_scale.bandwidth() / 2)
                        .attr("y", d => this.y_scale(d.y_step) + this.y_scale.bandwidth() / 2)
                        .style("font-weight", d => (d.type == "total" ? "bold" : null));

                    return g;
                },
                update => update,
                exit => exit.call(exit => exit.transition().remove())
            )
            .call(g => {
                // operate the d3 selection merge of enter + update

                // add transition to prevent too many DOM transforms at once
                let t = g.transition();
                if (data.length < 100) {
                    t.delay((_, i) => i * 5);
                } else {
                    t.delay((_, i) => i * 1);
                }

                g.select("rect")
                    .transition(t)
                    .style("fill", d => (d.type == "cell" ? cellColor(d) : totalColor(d)));

                g.select("text")
                    .transition(t)
                    .style("fill", textColor)
                    .style("display", d => (d.rows.length == 0 ? "none" : null))
                    .text(d => (showCounts == 1 ? this.store.getCount(d.rows) : "＋"));

                this.bind_tooltip(g, "cell");
            });
    };

    build_plot() {
        const {settings} = this.store;

        // Clear plot div and and append new svg object
        this.plot_div.empty();
        this.svg = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("role", "image")
            .attr("aria-label", "An exploratory heatmap graphic")
            .attr("class", "d3")
            .node();
        this.vis = d3.select(this.svg).append("g");

        this.cellDimensions = this.get_cell_dimensions();
        this.w = this.cellDimensions.width * this.x_steps;
        this.h = this.cellDimensions.height * this.y_steps;

        // Scales for x axis and y axis
        this.x_scale = d3.scaleBand().domain(_.range(0, this.x_steps)).range([0, this.w]);
        this.y_scale = d3.scaleBand().domain(_.range(0, this.y_steps)).range([0, this.h]);

        // Draw cells
        this.vis.append("g").attr("class", "exp_heatmap_cells");

        // draw the cells
        autorun(() => this.update_plot(this.store.matrixDataset));

        // Draw axes
        this.build_axes();

        // Draw labels
        this.build_labels();

        // Position plot
        this.vis.attr(
            "transform",
            `translate(${settings.padding.left + this.x_axis_label_padding},${
                settings.padding.top
            })`
        );

        this.add_grid();
        this.add_resize_and_toolbar();
    }

    add_resize_and_toolbar() {
        const {settings} = this.store,
            nativeSize = {
                width: Math.ceil(
                    settings.padding.left +
                        this.x_axis_label_padding +
                        this.w +
                        settings.padding.right
                ),
                height: Math.ceil(
                    settings.padding.top +
                        this.h +
                        this.y_axis_label_padding +
                        settings.padding.bottom
                ),
            },
            div = $("<div>")
                .css({
                    position: "relative",
                    display: "block",
                    top: "-30px",
                    left: "-3px",
                })
                .appendTo(this.plot_div);

        const yOffset = settings.x_axis_bottom ? 0 : -this.y_axis_label_padding;
        d3.select(this.svg)
            .attr("preserveAspectRatio", "xMidYMin meet")
            .attr("viewBox", `0 ${yOffset} ${nativeSize.width} ${nativeSize.height}`);

        ReactDOM.render(<VisualToolbar svg={this.svg} nativeSize={nativeSize} />, div[0]);
    }
}

export default ExploreHeatmapPlot;
