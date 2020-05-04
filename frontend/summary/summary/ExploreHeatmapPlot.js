import _ from "lodash";
import d3 from "d3";
import D3Visualization from "./D3Visualization";
import h from "shared/utils/helpers";
import HAWCModal from "utils/HAWCModal";

class ExploreHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        super(...arguments);
        this.generate_properties(data);
    }

    render($div) {
        this.build_elements($div);
        this.build_plot();
        this.build_axes();
        this.build_blacklist();
        this.build_labels();
        this.position_plot();
        this.set_viewbox();
        this.build_detail_box();
    }

    generate_properties(data) {
        // From constructor parameters
        this.dataset = data.dataset;
        _.assign(this, data.settings);
        this.blacklist = [];

        _.assign(this.plot, {top: 0, left: 0, bottom: 0, right: 0});

        this.horizontal_margin = 200;
        this.vertical_margin = 50;
        this.blacklist_domain = _.chain(this.dataset)
            .map(d => d[this.blacklist_field])
            .uniq()
            .sort()
            .value();

        this.blacklist_map = _.chain(this.blacklist_domain)
            .map(d => ({
                [this.blacklist_field]: d,
            }))
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
        this.xy_map = this.create_map();
    }

    build_elements($div) {
        const PLOT_WIDTH_MIN = 600,
            PLOT_HEIGHT_MIN = 400;

        let content_size = h.getHawcContentSize();

        if (typeof this.plot.width == "undefined")
            this.plot.width = Math.max(content_size.width, PLOT_WIDTH_MIN);
        if (typeof this.plot.height == "undefined")
            this.plot.height = Math.max(content_size.height, PLOT_HEIGHT_MIN);

        this.viz_container = d3.select($div.html("")[0]);
        this.svg = this.viz_container
            .append("svg")
            .attr("class", "d3")
            .attr("width", this.plot.width)
            .attr("height", this.plot.height);

        this.modal = new HAWCModal();
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
        if (!this.show_blacklist) return;
        this.plot.right += 100;
        let cell_width = this.horizontal_margin,
            func = d => {
                let in_list = _.includes(this.blacklist, d);
                in_list ? _.pull(this.blacklist, d) : this.blacklist.push(d);
                in_list = !in_list;
                this.xy_map = this.create_map();
                //this.xy_map = [];
                this.update_plot();
                return in_list;
            };
        this.blacklist_width = Math.ceil(this.blacklist_domain.length / this.y_steps) * cell_width;
        this.blacklist_group = this.plot_svg
            .append("g")
            .attr("id", "exp_heatmap_blacklist_cells")
            .attr("transform", `translate(${this.plot.width + this.plot.right},0)`);
        let blacklist_data = this.blacklist_group.selectAll("g").data(this.blacklist_domain),
            blacklist_enter = blacklist_data
                .enter()
                .append("g")
                .attr("class", "exp_heatmap_blacklist_cell")
                .on("click", function(d) {
                    d3.select(this).style("text-decoration", func(d) ? "line-through" : null);
                });
        blacklist_enter
            .append("rect")
            .attr("class", "exp_heatmap_blacklist_cell_block")
            .attr("x", (d, i) => cell_width * Math.floor(i / this.y_steps))
            .attr("y", (d, i) => {
                return this.y_scale(i % this.y_steps);
            })
            .attr("width", cell_width)
            .attr("height", this.y_scale.rangeBand())
            .style("fill", "white");
        blacklist_enter
            .append("text")
            .attr("class", "exp_heatmap_blacklist_cell_text")
            .attr("x", (d, i) => cell_width * Math.floor(i / this.y_steps))
            .attr("y", (d, i) => {
                return this.y_scale(i % this.y_steps);
            })
            .text(d => d);
        this.plot.right += this.blacklist_width;
    }

    build_detail_box() {
        let table = d3.select(this.modal.getBody()[0]).append("table");
        this.build_table(table, this.dataset);
    }

    build_table = (table, data, func) => {
        let header = this.all_fields;
        // Create table header
        table
            .append("thead")
            .append("tr")
            .selectAll("th")
            .data(header)
            .enter()
            .append("th")
            .text(d => d);
        // Fill in body
        table.append("tbody");
        this.fill_table(table, data, func);
    };

    fill_table = (table, data, func) => {
        let selection = table.selectAll("thead>tr>th"),
            header = selection[0].map(e => e.innerText),
            tbody = table.select("tbody"),
            rows = tbody.selectAll("tr").data(data);
        rows.enter().append("tr");
        rows.exit().remove();
        let row_data = rows.selectAll("td").data(d => header.map(e => d[e]));
        row_data.enter().append("td");
        row_data.exit().remove();
        row_data.text(d => d).on("click", func);
    };

    build_axes() {
        let x_domains = this.x_domain.map((e, i) => {
                let length = i == 0 ? 1 : this.x_domain[i - 1].length;
                for (let j = 1; j < length; j++) {
                    e = e.concat(e);
                }
                return e;
            }),
            y_domains = this.y_domain.map((e, i) => {
                let length = i == 0 ? 1 : this.y_domain[i - 1].length;
                for (let j = 1; j < length; j++) {
                    e = e.concat(e);
                }
                return e;
            });

        let x_axes = x_domains.map((element, index) => {
                return d3.svg
                    .axis()
                    .scale(
                        d3.scale
                            .ordinal()
                            .domain(_.range(0, element.length))
                            .rangeBands([0, this.plot.width])
                    )

                    .tickFormat(d => x_domains[index][d])
                    .outerTickSize(2)
                    .innerTickSize(10)
                    .orient("bottom");
            }),
            y_axes = y_domains.map((element, index) => {
                return d3.svg
                    .axis()
                    .scale(
                        d3.scale
                            .ordinal()
                            .domain(_.range(0, element.length))
                            .rangeBands([0, this.plot.height])
                    )
                    .tickFormat(d => y_domains[index][d])
                    .outerTickSize(2)
                    .innerTickSize(10)
                    .orient("left");
            });

        let x_axes_group = this.plot_svg
                .append("g")
                .attr("transform", `translate(0,${this.plot.height})`),
            y_axes_group = this.plot_svg.append("g");

        for (let i = 0; i < x_axes.length; i++) {
            x_axes_group
                .append("g")
                .attr("class", "exp_heatmap_axis")
                .attr("transform", `translate(0,${this.vertical_margin * (x_axes.length - 1 - i)})`)
                .call(x_axes[i]);
            this.plot.bottom += this.vertical_margin;
        }

        for (let i = 0; i < y_axes.length; i++) {
            y_axes_group
                .append("g")
                .attr("class", "exp_heatmap_axis")
                .attr("transform", `translate(${this.horizontal_margin * i},0)`)
                .call(y_axes[i]);
            this.plot.left += this.horizontal_margin;
        }
    }

    build_labels() {
        let label_margin = 50,
            title_exists = false;

        // Plot title
        if (this.plot_title.length > 0) {
            this.plot_svg
                .append("text")
                .attr("id", "exp_heatmap_title")
                .attr("class", "exp_heatmap_label")
                .attr("x", this.plot.width / 2)
                .attr("y", -label_margin / 2)
                .text(this.plot_title);
            this.plot.top += label_margin;
            title_exists = true;
        }

        // X axis
        if (this.x_label.length > 0) {
            this.plot_svg
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr("x", this.plot.width / 2)
                .attr("y", this.plot.height + this.plot.bottom + label_margin / 2)
                .text(this.x_label);
            this.plot.bottom += label_margin;
        }
        // Y axis
        if (this.y_label.length > 0) {
            this.plot_svg
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr("x", 0)
                .attr("y", 0)
                .attr(
                    "transform",
                    `translate(${-(this.plot.left + label_margin / 2)},${this.plot.height /
                        2}) rotate(-90)`
                )
                .text(this.y_label);
            this.plot.left += label_margin;
        }

        // Blacklist title
        if (this.show_blacklist && this.blacklist_label.length > 0) {
            this.blacklist_group
                .append("text")
                .attr("class", "exp_heatmap_label")
                .attr("x", this.blacklist_width / 2)
                .attr("y", -label_margin / 2)
                .text(this.blacklist_label);
            this.plot.top += title_exists ? 0 : label_margin;
        }
    }

    update_plot = () => {
        let cells_data = this.cells.selectAll("g").data(this.xy_map),
            cells_enter = cells_data
                .enter()
                .append("g")
                .attr("class", "exp_heatmap_cell")
                .on("click", d => {
                    this.fill_table(d3.select(this.modal.getBody()[0]).select("table"), d.dataset);
                    this.modal
                        .addHeader(
                            `<h4>Records where ${_.keys(d.x_filter)
                                .map(k => `${k} = ${d.x_filter[k]}`)
                                .join(", ")} and ${_.keys(d.y_filter)
                                .map(k => `${k} = ${d.y_filter[k]}`)
                                .join(", ")}</h4>`
                        )
                        .addFooter("")
                        .show();
                    console.log(d);
                });

        // Update cell blocks
        cells_enter
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
        cells_data.select("rect").style("fill", d => {
            return this.color_scale(d.dataset.length);
        });

        // Update cell text
        cells_enter
            .append("text")
            .attr("class", "exp_heatmap_cell_text")
            .attr("x", d => {
                return this.x_scale(d.x_step) + this.x_scale.rangeBand() / 2;
            })
            .attr("y", d => {
                return this.y_scale(d.y_step) + this.y_scale.rangeBand() / 2;
            });
        cells_data
            .select("text")
            .style("display", d => (d.dataset.length == 0 ? "none" : null))
            .text(d => d.dataset.length);

        cells_data.exit().remove();
    };

    position_plot() {
        this.plot_svg.attr("transform", `translate(${this.plot.left},${this.plot.top})`);
    }

    set_viewbox() {
        let w = this.plot.left + this.plot.right + this.plot.width,
            h = this.plot.top + this.plot.bottom + this.plot.height;
        this.svg.attr("viewBox", `0 0 ${w} ${h}`);
    }

    build_plot() {
        this.plot_svg = this.svg.append("g");

        // Scales for x axis, y axis, and cell color
        this.x_scale = d3.scale
            .ordinal()
            .domain(_.range(0, this.x_steps))
            .rangeBands([0, this.plot.width]);
        this.y_scale = d3.scale
            .ordinal()
            .domain(_.range(0, this.y_steps))
            .rangeBands([0, this.plot.height]);
        this.color_scale = d3.scale
            .linear()
            .domain([
                0,
                this.xy_map.reduce(
                    (current_max, element) => Math.max(current_max, element.dataset.length),
                    0
                ),
            ])
            .range(["white", "red"]);

        this.cells = this.plot_svg.append("g").attr("id", "exp_heatmap_cells");

        // Draw cells
        this.update_plot();
    }
}

export default ExploreHeatmapPlot;
