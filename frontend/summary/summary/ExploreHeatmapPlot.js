import _ from "lodash";
import d3 from "d3";
import D3Visualization from "./D3Visualization";
import h from "shared/utils/helpers";
import HAWCModal from "utils/HAWCModal";

class ExploreHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        super(...arguments);
        this.generate_properties(data);
        this.modal = new HAWCModal();
    }

    render($div) {
        this.build_container($div);
        this.render_plot($("#exp_heatmap_svg_container"));
        this.build_blacklist();
        this.build_detail_box();
    }

    render_plot($div) {
        this.plot_div = $div;
        this.set_color_scale();
        this.build_plot();
        if (this.show_grid) this.add_grid();
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

    set_color_scale() {
        this.color_scale = d3.scale
            .linear()
            .domain([
                0,
                this.cell_map.reduce(
                    (current_max, element) =>
                        Math.max(
                            current_max,
                            this.cell_dataset(element.x_filter, element.y_filter).length
                        ),
                    0
                ),
            ])
            .range(this.settings.color_range);
    }

    select_dataset() {
        if (this.selected_cells.length == 0) return this.filtered_dataset;
        return _.filter(this.filtered_dataset, e => {
            for (let cell of this.selected_cells) {
                if (_.isMatch(e, cell.x_filter) && _.isMatch(e, cell.y_filter)) return true;
            }
            return false;
        });
    }

    generate_properties(data) {
        this.settings = data.settings;
        this.padding = _.assign({}, this.settings.padding);
        this.show_grid = true;
        this.show_axis_border = true;

        // From constructor parameters
        this.dataset = data.dataset;
        this.filtered_dataset = this.dataset;
        this.selected_cells = [];
        this.blacklist = [];

        this.blacklist_domain = _.chain(this.dataset)
            .map(d => d[this.blacklist_field])
            .uniq()
            .sort()
            .value();

        this.x_domain = this.settings.x_fields.map(e =>
            _.chain(this.dataset)
                .map(d => d[e])
                .uniq()
                .sort()
                .value()
        );
        this.y_domain = this.settings.y_fields.map(e =>
            _.chain(this.dataset)
                .map(d => d[e])
                .uniq()
                .sort()
                .reverse()
                .value()
        );
        this.x_steps = this.x_domain.reduce((total, element) => total * element.length, 1);
        this.y_steps = this.y_domain.reduce((total, element) => total * element.length, 1);
        this.w = this.settings.cell_width * this.x_steps;
        this.h = this.settings.cell_height * this.y_steps;
        this.cell_map = this.create_map();
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
            x_map =
                this.x_domain.length == 0
                    ? []
                    : _step_domain(this.x_domain, this.settings.x_fields, 0),
            y_map =
                this.y_domain.length == 0
                    ? []
                    : _step_domain(this.y_domain, this.settings.y_fields, 0),
            xy_map = x_map
                .map(x_element => {
                    return y_map.map(y_element => {
                        let new_element = {
                            x_filter: x_element.filter,
                            y_filter: y_element.filter,
                            x_step: x_element.step,
                            y_step: y_element.step,
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
            self.fill_detail_table(self.select_dataset());
        });
    }

    build_detail_box() {
        // Create detail container
        this.detail_container = this.viz_container
            .append("div")
            .attr("class", "exp_heatmap_container")
            .style("width", "100%")
            .style(
                "height",
                `${Math.max(
                    h.getHawcContentSize().height -
                        $(this.svg)
                            .parent()
                            .height(),
                    200
                )}px`
            )
            .style("overflow", "auto");

        // Create detail table
        this.detail_table = this.detail_container
            .append("table")
            .attr("class", "table table-striped table-bordered");

        // Create the table header
        this.detail_table
            .append("thead")
            .append("tr")
            .selectAll("th")
            .data(this.settings.all_fields)
            .enter()
            .append("th")
            .text(d => d);

        // Fill in table body
        this.detail_table.append("tbody");
        this.fill_detail_table(this.select_dataset());
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

    fill_detail_table = data => {
        // Fills detail table
        let rows = this.detail_table
            .select("tbody")
            .selectAll("tr")
            .data(data);
        rows.enter().append("tr");
        rows.exit().remove();
        let row_data = rows.selectAll("td").data(d => this.settings.all_fields.map(e => d[e]));
        row_data.enter().append("td");
        row_data.exit().remove();
        row_data.text(d => d);
    };

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
            if (this.show_axis_border) add_border();
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
            if (this.show_axis_border) add_border();
        }
    }

    add_grid() {
        // Draws lines on plot
        let grid = this.vis.append("g"),
            x_band = this.w / this.x_steps,
            y_band = this.h / this.y_steps;
        for (let i = 0; i <= this.x_steps; i++) {
            grid.append("line")
                .attr("x1", x_band * i)
                .attr("y1", 0)
                .attr("x2", x_band * i)
                .attr("y2", this.h)
                .style("stroke", "black");
        }
        for (let i = 0; i <= this.y_steps; i++) {
            grid.append("line")
                .attr("x1", 0)
                .attr("y1", y_band * i)
                .attr("x2", this.w)
                .attr("y2", y_band * i)
                .style("stroke", "black");
        }
    }

    build_labels() {
        // Plot title
        if (this.settings.title.text.length > 0) {
            d3.select(this.svg)
                .append("text")
                .attr("id", "exp_heatmap_title")
                .attr("class", "exp_heatmap_label")
                .attr(
                    "transform",
                    `translate(${this.settings.title.x},${this.settings.title.y}) rotate(${this.settings.title.rotate})`
                )
                .text(this.settings.title.text);
        }

        // X axis
        if (this.settings.x_label.text.length > 0) {
            d3.select(this.svg)
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr(
                    "transform",
                    `translate(${this.settings.x_label.x},${this.settings.x_label.y}) rotate(${this.settings.x_label.rotate})`
                )
                .text(this.settings.x_label.text);
        }
        // Y axis
        if (this.settings.y_label.text.length > 0) {
            d3.select(this.svg)
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr(
                    "transform",
                    `translate(${this.settings.y_label.x},${this.settings.y_label.y}) rotate(${this.settings.y_label.rotate})`
                )
                .text(this.settings.y_label.text);
        }
    }

    set_cell_behavior() {
        // Cell group click fills out details table
        let self = this;
        this.cells_enter
            .on("click", function(d) {
                d3.selectAll(".exp_heatmap_cell_block")
                    .style("stroke", "none")
                    .style("stroke-width", 2);
                d3.select(this)
                    .select("rect")
                    .style("stroke", "black")
                    .style("stroke-width", 2);
                self.selected_cells = [d];
                self.fill_detail_table(self.select_dataset());
            })
            .on("mouseover", null);
    }

    update_cell_rect() {
        // Cell rect fill based on number of records
        this.cells_data.select("rect").style("fill", d => {
            return this.color_scale(this.cell_dataset(d.x_filter, d.y_filter).length);
        });
    }

    update_cell_text() {
        // Cell text shows number of records
        this.cells_data
            .select("text")
            .style("display", d =>
                this.cell_dataset(d.x_filter, d.y_filter).length == 0 ? "none" : null
            )
            .text(d => this.cell_dataset(d.x_filter, d.y_filter).length);
    }

    cell_dataset(x_filter, y_filter) {
        return _.filter(
            this.filtered_dataset,
            e => _.isMatch(e, x_filter) && _.isMatch(e, y_filter)
        );
    }

    update_plot = () => {
        /// Cell group behavior
        // On enter
        this.cells_data = this.cells.selectAll("g").data(this.cell_map);
        this.cells_enter = this.cells_data
            .enter()
            .append("g")
            .attr("class", "exp_heatmap_cell");
        this.set_cell_behavior();

        /// Cell rect behavior
        // On enter
        this.cells_enter
            .append("rect")
            .attr("class", "exp_heatmap_cell_block")
            .attr("x", d => {
                return this.x_scale(d.x_step);
            })
            .attr("y", d => {
                return this.y_scale(d.y_step);
            })
            .attr("width", this.x_scale.rangeBand())
            .attr("height", this.y_scale.rangeBand());
        // On update
        this.update_cell_rect();

        /// Cell text behavior
        // On enter
        this.cells_enter
            .append("text")
            .attr("class", "exp_heatmap_cell_text")
            .attr("x", d => {
                return this.x_scale(d.x_step) + this.x_scale.rangeBand() / 2;
            })
            .attr("y", d => {
                return this.y_scale(d.y_step) + this.y_scale.rangeBand() / 2;
            });
        this.cells_data.select("text").style("fill", d => {
            let {r, g, b} = d3.rgb(
                this.color_scale(this.cell_dataset(d.x_filter, d.y_filter).length)
            );
            ({r, g, b} = h.getTextContrastColor(r, g, b));
            return d3.rgb(r, g, b);
        });
        // On update
        this.update_cell_text();

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
