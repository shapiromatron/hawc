import _ from "lodash";
import d3 from "d3";
import D3Visualization from "./D3Visualization";

class ExploreHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        super(...arguments);
        this.generate_properties(data);
    }

    render($div) {
        this.build_elements($div);
        this.build_plot();
        this.build_axes();
        this.build_blacklist_sidebar();
        this.build_detail_box();
    }

    generate_properties(data) {
        // From constructor parameters
        this.dataset = data.dataset;
        _.assign(this, data.settings);
        this.blacklist = [];

        this.plot = _.assign({}, {width: 1200, height: 700});
        _.assign(this.plot, {top: 100, left: 100, bottom: 100, right: 100});

        this.blacklist_map = _.chain(this.dataset)
            .map(d => d[this.blacklist_field])
            .uniq()
            .sort()
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
                .value()
        );
        this.x_steps = this.x_domain.reduce((total, element) => total * element.length, 1);
        this.y_steps = this.y_domain.reduce((total, element) => total * element.length, 1);
        this.xy_map = this.create_map();
    }

    build_elements($div) {
        this.sidebar = {width: 200, height: this.plot.height};
        this.box = {width: this.plot.width + this.sidebar.width, height: 400};
        this.container = {width: this.box.width, height: this.plot.height + this.box.height};
        this.viz_container = $div.html("")[0];
        d3.select(this.viz_container)
            .style("width", `${this.container.width}px`)
            .style("height", `${this.container.height}px`)
            .style("outline-style", "solid");
        this.plot_container = d3
            .select(this.viz_container)
            .append("div")
            .style("float", "left")
            .style("width", `${this.plot.width}px`)
            .style("height", `${this.plot.height}px`)
            .style("outline-style", "solid");
        this.blacklist_container = d3
            .select(this.viz_container)
            .append("div")
            .style("float", "right")
            .style("width", `${this.sidebar.width}px`)
            .style("height", `${this.sidebar.height}px`)
            .style("outline-style", "solid");
        this.detail_container = d3
            .select(this.viz_container)
            .append("div")
            .attr("id", "viz-details")
            .style("clear", "both")
            .style("width", `${this.box.width}px`)
            .style("height", `${this.box.height}px`)
            .style("outline-style", "solid")
            .style("overflow", "scroll");
    }

    create_map = () => {
        let _step_domain = (domain, field, depth) => {
                if (depth >= domain.length - 1) {
                    return domain[depth].map((element, index) => {
                        return {filter: {[field[depth]]: element}, step: index + 1};
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

    build_blacklist_sidebar() {
        let table = this.blacklist_container.append("table"),
            func = d => {
                let in_list = _.includes(this.blacklist, d);
                in_list ? _.pull(this.blacklist, d) : this.blacklist.push(d);
                in_list = !in_list;
                this.xy_map = this.create_map();
                this.update_plot();
                return in_list;
            };

        this.build_table(table, this.blacklist_map, function(d) {
            d3.select(this).style("text-decoration", func(d) ? "line-through" : null);
        });
    }

    build_detail_box() {
        let table = this.detail_container.append("table");
        this.build_table(table, this.dataset);
    }

    build_table = (table, data, func) => {
        let header = _.keys(data[0]);
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
                    .orient("bottom");
            }),
            y_axes = y_domains.map((element, index) => {
                return d3.svg
                    .axis()
                    .scale(
                        d3.scale
                            .ordinal()
                            .domain(_.range(0, element.length))
                            .rangeBands([this.plot.height, 0])
                    )
                    .tickFormat(d => y_domains[index][d])
                    .orient("left");
            });

        this.plot_svg
            .append("g")
            .attr("id", "x-axes")
            .attr("transform", `translate(0,${this.plot.height})`);

        for (let i = 0; i < x_axes.length; i++) {
            this.plot_svg
                .select("g#x-axes")
                .append("g")
                .attr("transform", `translate(0,${25 * (x_axes.length - i - 1)})`)
                .call(x_axes[i]);
        }

        this.plot_svg.append("g").attr("id", "y-axes");

        for (let i = 0; i < y_axes.length; i++) {
            this.plot_svg
                .select("g#y-axes")
                .append("g")
                .attr("transform", `translate(${25 * i},0)`)
                .call(y_axes[i]);
        }
    }

    update_plot = () => {
        let cells_data = this.cells.data(this.xy_map),
            cells_text_data = this.cells_text.data(
                _.filter(this.xy_map, e => e.dataset.length > 0)
            );
        // Update cells
        cells_data
            .enter()
            .append("rect")
            .attr("class", "cell")
            .attr("x", d => {
                return this.x_scale(d.x_step);
            })
            .attr("y", d => {
                return this.y_scale(d.y_step);
            })
            .attr("width", this.x_scale.rangeBand())
            .attr("height", this.y_scale.rangeBand())
            .style("stroke", "black")
            .style("stroke-width", "1")
            .append("text")
            .attr("x", d => {
                return this.x_scale(d.x_step);
            })
            .attr("y", d => {
                return this.y_scale(d.y_step);
            });
        cells_data.exit().remove();
        cells_data
            .style("fill", d => {
                return this.color_scale(d.dataset.length);
            })
            .on("click", d => this.fill_table(d3.select("div#viz-details>table"), d.dataset));

        // Update cells text
        cells_text_data
            .enter()
            .append("text")
            .attr("class", "cell")
            .attr("x", d => {
                return this.x_scale(d.x_step) + this.x_scale.rangeBand() / 2;
            })
            .attr("y", d => {
                return this.y_scale(d.y_step) + this.y_scale.rangeBand() / 2;
            })
            .style("text-anchor", "middle");
        cells_text_data.exit().remove();
        cells_text_data.text(d => d.dataset.length);
    };

    build_plot() {
        let w = this.plot.width + this.plot.left + this.plot.right,
            h = this.plot.height + this.plot.top + this.plot.bottom;
        this.plot_svg = this.plot_container
            .append("svg")
            .attr("class", "d3")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", `0 0 ${w} ${h}`)
            .append("g")
            .attr("transform", `translate(${this.plot.left},${this.plot.top})`);

        // Scales for x axis, y axis, and cell color
        this.x_scale = d3.scale
            .ordinal()
            .domain(_.range(1, this.x_steps + 1))
            .rangeBands([0, this.plot.width]);
        this.y_scale = d3.scale
            .ordinal()
            .domain(_.range(1, this.y_steps + 1))
            .rangeBands([this.plot.height, 0]);
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

        // D3 selection of cells & text
        this.cells = this.plot_svg
            .append("g")
            .attr("id", "cells")
            .selectAll("rect.cell");
        this.cells_text = this.plot_svg.select("g#cells").selectAll("text.cell");

        // Draw cells
        this.update_plot();

        // Axis labels
        this.plot_svg
            .append("text")
            .attr("x", this.plot.width / 2)
            .attr("y", this.plot.height + 0.75 * this.plot.bottom)
            .style("text-anchor", "middle")
            .text(this.x_label);
        this.plot_svg
            .append("text")
            .attr("x", 0)
            .attr("y", 0)
            .attr("transform", `translate(${-this.plot.left},${this.plot.height / 2}) rotate(-90)`)
            .style("text-anchor", "middle")
            .text(this.y_label);

        // Plot title
        this.plot_svg
            .append("text")
            .attr("x", this.plot.width / 2)
            .attr("y", -0.75 * this.plot.top)
            .style("text-anchor", "middle")
            .text(this.title);
    }
}

export default ExploreHeatmapPlot;
