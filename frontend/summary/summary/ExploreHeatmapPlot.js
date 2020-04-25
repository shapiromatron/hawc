import _ from "lodash";
import d3 from "d3";

import HAWCModal from "utils/HAWCModal";

import D3Visualization from "./D3Visualization";

class ExploreHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        // heatmap of rob information. Criteria are on the y-axis,
        // and studies are on the x-axis
        super(...arguments);
        this.data.settings.type = "heatmap";
        this.data.dataset = [
            {foo: "b", bar: "b", foobar: "b"},
            {foo: "c", bar: "a", foobar: "c"},
        ];
        this.modal = new HAWCModal();
    }

    render($div) {
        this.plot_div = $div.html("");
        this.assignProperties();

        this.draw_visualization();
    }

    assignProperties() {
        this.plot_width = 600;
        this.plot_height = 600;
        this.options = _.keys(this.data.dataset[0]);
        this.x_field = [this.options[0], this.options[1], this.options[2]];
        this.y_field = [this.options[0]];
        this.x_domain = this.x_field.map(e =>
            _.chain(this.data.dataset)
                .map(d => d[e])
                .uniq()
                .sort()
                .value()
        );
        this.y_domain = this.y_field.map(e =>
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
            this.x_field,
            this.y_field,
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
        var w = 600,
            h = 600;
        this.vis = d3
            .select(this.plot_div[0])
            .append("svg")
            .attr("width", w)
            .attr("height", h)
            .attr("class", "d3")
            .attr("viewBox", `0 0 ${w} ${h}`)
            .attr("preserveAspectRatio", "xMinYMin");

        var axis_b = d3.scale
            .ordinal()
            .domain(_.range(1, this.x_steps + 2))
            .rangeBands([0, this.plot_width]);

        this.vis
            .append("text")
            .attr("x", this.plot_width / 2)
            .attr("y", this.plot_height)
            .style("text-anchor", "middle")
            .text(this.x_field);

        var axis_l = d3.scale
            .ordinal()
            .domain(_.range(1, this.y_steps + 2))
            .rangeBands([this.plot_height, 0]);

        this.vis
            .append("text")
            .attr("x", 0)
            .attr("y", 0)
            .attr("transform", `translate(0,${this.plot_height / 2}) rotate(-90)`)
            .style("text-anchor", "middle")
            .text(this.y_field);

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
            .style("stroke", "white")
            .style("stroke-width", "5");
    }
}

export default ExploreHeatmapPlot;
