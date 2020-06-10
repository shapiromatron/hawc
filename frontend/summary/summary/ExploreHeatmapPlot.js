import _ from "lodash";
import d3 from "d3";
import D3Visualization from "./D3Visualization";
import h from "shared/utils/helpers";
import HAWCModal from "utils/HAWCModal";

import React from "react";
import ReactDOM from "react-dom";
import HeatmapDatastore from "./heatmap/HeatmapDatastore";
import DatasetTable from "./heatmap/DatasetTable";

class ExploreHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        super(...arguments);
        this.generate_properties(data);
        this.store = new HeatmapDatastore(data.settings, data.dataset);
        this.modal = new HAWCModal();
        this.datasetTable = new DatasetTable(this.store);
    }

    render($div) {
        this.build_container($div);
        this.render_plot($("#exp_heatmap_svg_container"));
        this.build_blacklist();
        // this.datasetTable.renderTable(this.viz_container, this.svg);
        const tblDiv = $("<div>").appendTo($(this.viz_container[0][0]));
        ReactDOM.render(<DatasetTable store={this.store} />, tblDiv.get(0));
    }

    render_plot($div) {
        this.plot_div = $div;
        this.build_plot();
        this.add_grid();
        this.set_trigger_resize();
        this.add_menu();
    }

    set_trigger_resize() {
        var self = this,
            w = this.w + this.padding.left + this.padding.right,
            h = this.h + this.padding.top + this.padding.bottom,
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

    update_detail_table(d) {
        const data = d.rows.map(index => this.filtered_dataset[index]);
        this.store.updateSelectedTableData(data);
    }

    select_dataset() {
        // filters dataset to what a user has selected.
        if (this.selected_cells.length == 0) {
            return this.filtered_dataset;
        }

        return _.filter(this.filtered_dataset, e => {
            for (let cell of this.selected_cells) {
                if (_.isMatch(e, cell.x_filter) && _.isMatch(e, cell.y_filter)) {
                    return true;
                }
            }
            return false;
        });
    }

    generate_properties(data) {
        this.cell_width = 50;
        this.cell_height = 50;
        this.padding = {top: 0, left: 0, bottom: 0, right: 200};
        this.show_grid = true;
        this.show_axis_border = true;
        this.x_rotate = 90;
        this.y_rotate = 0;

        // From constructor parameters
        this.dataset = data.dataset;
        this.filtered_dataset = this.dataset;
        this.processedData = this.preprocess_data(data.dataset, data.settings);
        _.assign(this, data.settings);
        this.blacklist = [];

        this.blacklist_domain = _.chain(this.dataset)
            .map(d => d[this.blacklist_field])
            .uniq()
            .sort()
            .value();

        this.x_domain = this.x_fields_new.map(e =>
            _.keys(this.processedData.intersection[e.column])
        );
        this.y_domain = this.y_fields_new.map(e =>
            _.keys(this.processedData.intersection[e.column])
        );
        this.x_steps = this.x_domain.reduce((total, element) => total * element.length, 1);
        this.y_steps = this.y_domain.reduce((total, element) => total * element.length, 1);
        this.w = this.cell_width * this.x_steps;
        this.h = this.cell_height * this.y_steps;
        this.cell_map = this.create_map();

        // set colorscale
        this.color_scale = d3.scale
            .linear()
            .domain([0, d3.max(this.cell_map, d => d.rows.length)])
            .range(this.color_range);
    }

    preprocess_data(dataset, settings) {
        /*
        here, we have "red" in the color column with element index 1, 2, and 3
        intersection["color"]["red"] = Set([1,2,3])
        */
        let intersection = {},
            addColumnsToMap = row => {
                const columnName = row.column,
                    delimiter = row.delimiter;
                // create column array if needed
                if (intersection[columnName] === undefined) {
                    intersection[columnName] = {};
                }
                dataset.forEach((d, idx) => {
                    const values =
                        delimiter !== "" ? d[columnName].split(delimiter) : [d[columnName]];
                    for (let value of values) {
                        if (intersection[columnName][value] === undefined) {
                            intersection[columnName][value] = [];
                        }
                        intersection[columnName][value].push(idx);
                    }
                });
            };

        settings.x_fields_new.map(addColumnsToMap);
        settings.y_fields_new.map(addColumnsToMap);

        // convert arrays to Sets
        _.each(intersection, (dataColumn, columnName) => {
            _.each(dataColumn, (rows, value) => {
                dataColumn[value] = new Set(rows);
            });
        });

        return {intersection};
    }

    build_container($div) {
        // Create svg container
        this.viz_container = d3.select($div.html("")[0]);
        this.svg_blacklist_container = this.viz_container
            .append("div")
            .style("white-space", "nowrap");
        this.svg_container = this.svg_blacklist_container
            .append("div")
            .style("display", "inline-block")
            .style("width", "80%")
            .style("vertical-align", "top")
            .attr("id", "exp_heatmap_svg_container");
    }

    create_map = () => {
        let _step_domain = (domain, field, depth) => {
                if (depth == domain.length - 1) {
                    return domain[depth].map((element, index) => {
                        return {filter: {[field[depth]]: element}, step: index};
                    });
                } else {
                    return domain[depth]
                        .map((element, index) => {
                            let inner = _step_domain(domain, field, depth + 1);
                            return inner.map((inner_element, inner_index) => {
                                inner_element["filter"][field[depth]] = element;
                                inner_element["step"] += index * inner.length;
                                return inner_element;
                            });
                        })
                        .flat();
                }
            },
            getIntersection = function(arr, set2) {
                return arr.filter(x => set2.has(x));
            },
            {intersection} = this.processedData,
            getRows = filters => {
                let rows = [];
                _.each(_.keys(filters), (columnName, idx) => {
                    if (idx === 0) {
                        rows = [...intersection[columnName][filters[columnName]]];
                    } else {
                        rows = getIntersection(rows, intersection[columnName][filters[columnName]]);
                    }
                });
                return rows;
            },
            x_map = _step_domain(this.x_domain, this.x_fields, 0),
            y_map = _step_domain(this.y_domain, this.y_fields, 0),
            xy_map = x_map
                .map(x_element => {
                    return y_map.map(y_element => {
                        let new_element = {
                            x_filter: x_element.filter,
                            y_filter: y_element.filter,
                            x_step: x_element.step,
                            y_step: y_element.step,
                            rows: getRows(Object.assign({}, x_element.filter, y_element.filter)),
                        };
                        return new_element;
                    });
                })
                .flat();
        return xy_map;
    };

    build_blacklist() {
        // Create blacklist container
        this.blacklist_container = this.svg_blacklist_container
            .insert("div", ":first-child")
            .attr("class", "exp_heatmap_container")
            .style("width", "20%")
            .style(
                "height",
                `${$(this.svg)
                    .parent()
                    .height()}px`
            )
            .style("vertical-align", "top")
            .style("display", "inline-block")
            .style("overflow", "auto");

        // Have resize trigger also resize blacklist container
        let old_trigger = this.trigger_resize;
        this.trigger_resize = forceResize => {
            old_trigger(forceResize);
            this.blacklist_container.style(
                "height",
                `${$(this.svg)
                    .parent()
                    .height()}px`
            );
        };
        $(window).resize(this.trigger_resize);

        let self = this,
            blacklist_select = this.blacklist_container.append("div").attr("class", "btn-group"),
            blacklist_input = this.blacklist_container.append("div"),
            blacklist_enter = blacklist_input
                .selectAll("input")
                .data(this.blacklist_domain)
                .enter()
                .append("div"),
            blacklist_label = blacklist_enter.append("label"),
            detail_handler = d => {
                this.modal
                    .addHeader(`<h4>${d}</h4>`)
                    .addFooter("")
                    .show();
            };

        // Button to check all boxes
        blacklist_select
            .append("button")
            .attr("class", "btn")
            .text("All")
            .on("click", () => {
                blacklist_input.selectAll("label").each(function() {
                    d3.select(this)
                        .select("input")
                        .property("checked", true);
                });
                blacklist_input.node().dispatchEvent(new Event("change"));
            });
        // Button to uncheck all boxes
        blacklist_select
            .append("button")
            .attr("class", "btn")
            .text("None")
            .on("click", () => {
                blacklist_input.selectAll("label").each(function() {
                    d3.select(this)
                        .select("input")
                        .property("checked", false);
                });
                blacklist_input.node().dispatchEvent(new Event("change"));
            });

        // Before each label is a detail button
        blacklist_enter
            .insert("button", ":first-child")
            .attr("class", "btn btn-mini pull-left")
            .on("click", detail_handler)
            .html("<i class='icon-eye-open'></i>");

        // Each label has a checkbox and the value of the blacklisted item
        blacklist_label
            .append("input")
            .attr("type", "checkbox")
            .property("checked", true);
        blacklist_label.append("span").text(d => d);
        blacklist_input.on("change", function() {
            self.blacklist = [];
            d3.select(this)
                .selectAll("label")
                .each(function(d) {
                    if (
                        !d3
                            .select(this)
                            .select("input")
                            .property("checked")
                    )
                        self.blacklist.push(d);
                });
            self.filter_dataset();
            self.update_plot();
            // this.datasetTable.updateTableBody(data);
        });
    }

    filter_dataset() {
        if (this.blacklist.length > 0) {
            this.filtered_dataset = _.filter(
                this.dataset,
                e => !_.includes(this.blacklist, e[this.blacklist_field])
            );
        } else {
            this.filtered_dataset = this.dataset;
        }
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
                    .attr("transform", `rotate(${this.x_rotate})`)
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
            this.padding.bottom += max;
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
            if (this.show_axis_border) {
                add_border();
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
                    .attr("transform", `rotate(${this.y_rotate})`)
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
            this.padding.left += max;
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
            if (this.show_axis_border) {
                add_border();
            }
        }
    }

    add_grid() {
        if (!this.show_grid) {
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
        if (this.plot_title.length > 0) {
            this.vis
                .append("text")
                .attr("id", "exp_heatmap_title")
                .attr("class", "exp_heatmap_label")
                .attr("x", this.w / 2)
                .attr("y", -this.label_margin / 2)
                .text(this.plot_title);
            this.padding.top += this.label_margin;
        }

        // X axis
        if (this.x_label.length > 0) {
            this.padding.bottom += this.label_margin;
            this.vis
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr("x", this.w / 2)
                .attr("y", this.h + this.padding.bottom - this.label_margin / 2)
                .text(this.x_label);
        }
        // Y axis
        if (this.y_label.length > 0) {
            this.padding.left += this.label_margin;
            this.vis
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr("x", 0)
                .attr("y", 0)
                .attr(
                    "transform",
                    `translate(${-(this.padding.left - this.label_margin / 2)},${this.h /
                        2}) rotate(-90)`
                )
                .text(this.y_label);
        }
    }

    update_plot = () => {
        const self = this,
            cell_group = this.cells.selectAll("g").data(this.cell_map);

        // add cell group and interactivity
        this.cells_enter = cell_group
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

                self.update_detail_table(d);
            })
            .on("mouseover", null);

        // add cell fill
        this.cells_enter
            .append("rect")
            .attr("class", "exp_heatmap_cell_block")
            .attr("x", d => this.x_scale(d.x_step))
            .attr("y", d => this.y_scale(d.y_step))
            .attr("width", this.x_scale.rangeBand())
            .attr("height", this.y_scale.rangeBand())
            .style("fill", d => this.color_scale(d.rows.length));

        /// add cell text
        this.cells_enter
            .append("text")
            .attr("class", "exp_heatmap_cell_text")
            .attr("x", d => this.x_scale(d.x_step) + this.x_scale.rangeBand() / 2)
            .attr("y", d => this.y_scale(d.y_step) + this.y_scale.rangeBand() / 2)
            .style("fill", d => {
                let {r, g, b} = d3.rgb(this.color_scale(d.rows.length));
                ({r, g, b} = h.getTextContrastColor(r, g, b));
                return d3.rgb(r, g, b);
            })
            .style("display", d => (d.rows.length == 0 ? "none" : null))
            .text(d => d.rows.length);
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
        this.cells = this.vis.append("g").attr("id", "exp_heatmap_cells");
        this.update_plot();

        // Draw axes
        this.build_axes();

        // Draw labels
        this.build_labels();

        // Set plot dimensions and viewbox
        let w = this.w + this.padding.left + this.padding.right,
            h = this.h + this.padding.top + this.padding.bottom;
        d3.select(this.svg)
            .attr("width", w)
            .attr("height", h)
            .attr("viewBox", `0 0 ${w} ${h}`);

        // Position plot
        this.vis.attr("transform", `translate(${this.padding.left},${this.padding.top})`);
    }
}

export default ExploreHeatmapPlot;
