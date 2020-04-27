import _ from "lodash";
import d3 from "d3";
import h from "shared/utils/helpers";
import D3Visualization from "./D3Visualization";

class ExploreHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        super(...arguments);
        this.data.settings = {
            type: "heatmap",
            title: "Exploratory heatmap of experiments by species, sex, and health system",
            x_axis_label: "Species & Sex",
            y_axis_label: "Health System",
        };
        this.data.options = {
            x_fields: ["species-name", "animal_group-sex"], //nested fields on x axis
            y_fields: ["endpoint-system"], //nested fields on y axis
            //all_fields: ["foo", "bar"], //all fields we are interested in, ignore excluded fields on detail page
            filter: "study-short_citation", //additional filter(s?) / main identifier
        };
        this.data.dataset = require("./test-json.json");
    }

    render($div) {
        this.generateProperties($div);
        this.draw_visualization();
    }

    generateProperties($div) {
        this.plot = _.assign({}, h.getHawcContentSize());
        this.plot.div = $div.html("")[0];
        this.x_domain = this.data.options.x_fields.map(e =>
            _.chain(this.data.dataset)
                .map(d => d[e])
                .uniq()
                .sort()
                .value()
        );
        this.y_domain = this.data.options.y_fields.map(e =>
            _.chain(this.data.dataset)
                .map(d => d[e])
                .uniq()
                .sort()
                .value()
        );
        this.x_steps = this.x_domain.reduce((total, element) => total * element.length, 1);
        this.y_steps = this.y_domain.reduce((total, element) => total * element.length, 1);
        this.xy_map = this.create_map(
            this.data.dataset,
            this.data.options.x_fields,
            this.data.options.y_fields,
            this.x_domain,
            this.y_domain
        );
    }

    create_map(dataset, x_field, y_field, x_domain, y_domain) {
        function _step_domain(domain, field, depth) {
            if (depth >= domain.length - 1) {
                return domain[depth].map(function(element, index) {
                    return {filter: {[field[depth]]: element}, step: index + 1};
                });
            } else {
                return domain[depth]
                    .map(function(element, index) {
                        let inner = _step_domain(domain, field, depth + 1);
                        return inner.map(function(inner_element, inner_index) {
                            inner_element["filter"][field[depth]] = element;
                            inner_element["step"] += index * inner.length;
                            return inner_element;
                        });
                    })
                    .flat();
            }
        }
        let x_map = _step_domain(x_domain, x_field, 0),
            y_map = _step_domain(y_domain, y_field, 0),
            xy_map = x_map
                .map(function(x_element) {
                    return y_map.map(function(y_element) {
                        let new_element = {
                            x_filter: x_element.filter,
                            y_filter: y_element.filter,
                            x_step: x_element.step,
                            y_step: y_element.step,
                        };
                        new_element["dataset"] = _.filter(
                            dataset,
                            _.matches(
                                _.assign({}, new_element["x_filter"], new_element["y_filter"])
                            )
                        );
                        return new_element;
                    });
                })
                .flat();
        console.log(xy_map);

        return xy_map;
    }

    draw_visualization() {
        this.vis = d3
            .select(this.plot.div)
            .append("svg")
            .attr("width", this.plot.width)
            .attr("height", this.plot.height)
            .attr("class", "d3")
            .attr("viewBox", `0 0 ${this.plot.width} ${this.plot.height}`)
            .attr("preserveAspectRatio", "xMinYMin");

        var axis_b = d3.scale
            .ordinal()
            .domain(_.range(1, this.x_steps + 2))
            .rangeBands([0, this.plot.width]);

        this.vis
            .append("text")
            .attr("x", this.plot.width / 2)
            .attr("y", this.plot.height)
            .style("text-anchor", "middle")
            .text(this.data.options.x_fields);

        var axis_l = d3.scale
            .ordinal()
            .domain(_.range(1, this.y_steps + 2))
            .rangeBands([this.plot.height, 0]);

        this.vis
            .append("text")
            .attr("x", 0)
            .attr("y", 0)
            .attr("transform", `translate(0,${this.plot.height / 2}) rotate(-90)`)
            .style("text-anchor", "middle")
            .text(this.data.options.y_fields);

        this.vis
            .append("g")
            .selectAll("dot")
            .data(this.xy_map)
            .enter()
            .append("rect")
            .attr("x", function(d) {
                return axis_b(d.x_step);
            })
            .attr("y", function(d) {
                return axis_l(d.y_step);
            })
            .attr("width", axis_b.rangeBand())
            .attr("height", axis_l.rangeBand())
            .style("fill", "white")
            .style("stroke", "black")
            .style("stroke-width", "1")
            .append("text")
            .attr("x", function(d) {
                return axis_b(d.x_step);
            })
            .attr("y", function(d) {
                return axis_l(d.y_step);
            })
            .text("test");
    }
}

export default ExploreHeatmapPlot;
