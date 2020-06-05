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
        this.build_axes();
        this.build_labels();
        this.set_trigger_resize();
        this.add_menu();
    }

    set_trigger_resize() {
        var self = this,
            w = this.w + this.padding.left + this.padding.right,
            h = this.h + this.padding.top + this.padding.bottom,
            chart = $(this.svg),
            container = chart.parent();

        d3.select(this.svg)
            .attr("width", w)
            .attr("height", h)
            .attr("viewBox", `0 0 ${w} ${h}`);

        this.vis.attr("transform", `translate(${this.padding.left},${this.padding.top})`);

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
                this.xy_map.reduce(
                    (current_max, element) => Math.max(current_max, element.dataset.length),
                    0
                ),
            ])
            .range(this.color_range);
    }

    generate_properties(data) {
        // From constructor parameters
        this.dataset = data.dataset;
        _.assign(this, data.settings);
        this.blacklist = [];

        this.blacklist_domain = _.chain(this.dataset)
            .map(d => d[this.blacklist_field])
            .uniq()
            .sort()
            .value();

        this.x_domain = this.x_fields.map(e =>
            _.chain(this.dataset)
                .map(d => d[e])
                .uniq()
                .sort()
                .value()
        );
        this.y_domain = this.y_fields.map(e =>
            _.chain(this.dataset)
                .map(d => d[e])
                .uniq()
                .sort()
                .reverse()
                .value()
        );
        this.x_steps = this.x_domain.reduce((total, element) => total * element.length, 1);
        this.y_steps = this.y_domain.reduce((total, element) => total * element.length, 1);
        this.cell_width = 100;
        this.cell_height = 100;
        this.w = this.cell_width * this.x_steps;
        this.h = this.cell_height * this.y_steps;
        this.padding = {top: 0, left: 0, bottom: 0, right: 200};
        this.xy_map = this.create_map();
    }
    build_container($div) {
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
                        };
                        new_element["dataset"] = _.filter(
                            this.dataset,
                            _.matches(
                                _.assign({}, new_element["x_filter"], new_element["y_filter"])
                            )
                        );
                        if (this.blacklist.length > 0) {
                            new_element["dataset"] = _.filter(
                                new_element["dataset"],
                                e => !_.includes(this.blacklist, e[this.blacklist_field])
                            );
                        }
                        return new_element;
                    });
                })
                .flat();

        return xy_map;
    };

    build_blacklist() {
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

        this.blacklist_table = this.blacklist_container
            .append("table")
            .attr("class", "table table-striped table-bordered table-hover");
        let func = d => {
            let in_list = _.includes(this.blacklist, d);
            in_list ? _.pull(this.blacklist, d) : this.blacklist.push(d);
            in_list = !in_list;
            this.xy_map = this.create_map();
            this.update_plot();
            return in_list;
        };

        // Create the table header
        this.blacklist_table
            .append("thead")
            .append("tr")
            .append("th")
            .text(this.blacklist_field);
        // Fill in table body
        this.blacklist_table.append("tbody");

        let modal_table = d3.select(this.modal.getBody()[0]).append("table"),
            button_func = d => {
                d3.event.stopPropagation();
                this.modal
                    .addHeader(`<h4>Test</h4>`)
                    .addFooter("")
                    .show();
            };

        let rows = this.blacklist_table
            .select("tbody")
            .selectAll("tr")
            .data(this.blacklist_domain);
        rows.enter()
            .append("tr")
            .append("td")
            .text(d => d)
            .on("click", function(d) {
                d3.select(this).style("text-decoration", func(d) ? "line-through" : null);
            })
            .append("button")
            .attr("class", "btn btn-mini pull-right")
            .on("click", button_func)
            .html("<i class='icon-eye-open'></i>");

        this.blacklist_table.selectAll("th").attr("colspan", 2);
        this.blacklist_table.selectAll("td").attr("colspan", 2);

        let mass_select = this.blacklist_table.select("tbody").insert("tr", ":first-child"),
            select_all = mass_select
                .append("td")
                .style("width", "50%")
                .on("click", d => {
                    this.blacklist_table.selectAll("tbody>tr+tr>td").style("text-decoration", null);
                    this.blacklist = [];
                    this.xy_map = this.create_map();
                    this.update_plot();
                })
                .text("All"),
            select_none = mass_select
                .append("td")
                .style("width", "50%")
                .on("click", d => {
                    this.blacklist_table
                        .selectAll("tbody>tr+tr>td")
                        .style("text-decoration", "line-through");
                    this.blacklist = this.blacklist_domain.slice();
                    this.xy_map = this.create_map();
                    this.update_plot();
                })
                .text("None");

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
    }

    build_detail_box() {
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

        this.detail_container.append("h4").text("Study Details");

        this.detail_table = this.detail_container
            .append("table")
            .attr("class", "table table-striped table-bordered");

        // Create the table header
        this.detail_table
            .append("thead")
            .append("tr")
            .selectAll("th")
            .data(this.all_fields)
            .enter()
            .append("th")
            .text(d => d);
        // Fill in table body
        this.detail_table.append("tbody");
        this.fill_detail_table(this.dataset);
    }

    fill_detail_table = data => {
        let rows = this.detail_table
            .select("tbody")
            .selectAll("tr")
            .data(data);
        rows.enter().append("tr");
        rows.exit().remove();
        let row_data = rows.selectAll("td").data(d => this.all_fields.map(e => d[e]));
        row_data
            .enter()
            .append("td")
            .append("input")
            .attr("type", "button")
            .attr("value", "a");
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
            label_padding = 10;

        this.x_rotate = 0;
        this.y_rotate = 0;

        for (let i = 0; i < x_domains.length; i++) {
            let axis = this.vis
                    .append("g")
                    .attr("transform", `translate(0,${this.h + x_axis_offset})`),
                domain = x_domains[i],
                band = this.w / domain.length,
                mid = band / 2,
                max = 0;
            for (let j = 0; j < domain.length; j++) {
                let label = axis.append("g"),
                    label_text = label
                        .append("text")
                        .attr("transform", `rotate(${this.x_rotate})`)
                        .text(domain[j]),
                    box = label.node().getBBox(),
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
        }

        for (let i = 0; i < y_domains.length; i++) {
            let axis = this.vis.append("g").attr("transform", `translate(${-y_axis_offset},0)`),
                domain = y_domains[i],
                band = this.h / domain.length,
                mid = band / 2,
                max = 0;
            for (let j = 0; j < domain.length; j++) {
                let label = axis.append("g"),
                    label_text = label
                        .append("text")
                        .attr("transform", `rotate(${this.y_rotate})`)
                        .text(domain[j]),
                    box = label.node().getBBox(),
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
        }
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

    set_cell_behavior() {
        let fill = d => this.fill_detail_table(d.dataset);
        this.cells_enter
            .on("click", function(d) {
                d3.selectAll(".exp_heatmap_cell_block")
                    .style("stroke", "none")
                    .style("stroke-width", 2);
                d3.select(this)
                    .select("rect")
                    .style("stroke", "black")
                    .style("stroke-width", 2);
                fill(d);
            })
            .on("mouseover", null);
    }

    update_cell_rect() {
        this.cells_data.select("rect").style("fill", d => {
            return this.color_scale(d.dataset.length);
        });
    }

    update_cell_text() {
        this.cells_data
            .select("text")
            .style("display", d => (d.dataset.length == 0 ? "none" : null))
            .text(d => d.dataset.length);
    }

    update_plot = () => {
        this.cells_data = this.cells.selectAll("g").data(this.xy_map);
        this.cells_enter = this.cells_data
            .enter()
            .append("g")
            .attr("class", "exp_heatmap_cell");
        this.set_cell_behavior();

        // Update cell blocks
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
        this.update_cell_rect();

        // Update cell text
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
            let {r, g, b} = d3.rgb(this.color_scale(d.dataset.length));
            ({r, g, b} = h.getTextContrastColor(r, g, b));
            return d3.rgb(r, g, b);
        });
        this.update_cell_text();

        this.cells_data.exit().remove();
    };

    build_plot($div) {
        //clear plot div and and append new svg object
        this.plot_div.empty();
        this.vis = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("class", "d3")
            .attr("preserveAspectRatio", "xMinYMin")
            .append("g");
        this.svg = this.vis[0][0].parentNode;

        // Scales for x axis, y axis, and cell color
        this.x_scale = d3.scale
            .ordinal()
            .domain(_.range(0, this.x_steps))
            .rangeBands([0, this.w]);
        this.y_scale = d3.scale
            .ordinal()
            .domain(_.range(0, this.y_steps))
            .rangeBands([0, this.h]);

        this.cells = this.vis.append("g").attr("id", "exp_heatmap_cells");

        // Draw cells
        this.update_plot();
    }
}

export default ExploreHeatmapPlot;
