import _ from "lodash";
import d3 from "d3";

import D3Visualization from "./D3Visualization";
import RoBLegend from "./RoBLegend";
import {SCORE_SHADES, NR_KEYS} from "riskofbias/constants";

class RoBBarchartPlot extends D3Visualization {
    constructor(parent, data, options) {
        // stacked-bars of rob information. Criteria are on the y-axis,
        // and studies are on the x-axis
        super(...arguments);
        this.setDefaults();
    }

    render($div) {
        this.plot_div = $div.html("");
        this.processData();
        if (this.dataset.length === 0) {
            let robName = this.data.assessment_rob_name.toLowerCase();
            return this.plot_div.html(
                `<p>Error: no studies with ${robName} selected. Please select at least one study with ${robName}.</p>`
            );
        }
        this.get_plot_sizes();
        this.build_plot_skeleton(true);
        this.add_axes();
        this.draw_visualizations();
        this.resize_plot_dimensions();
        this.trigger_resize();
        this.build_labels();
        this.add_menu();
        this.build_legend();
    }

    resize_plot_dimensions() {
        // Resize plot based on the dimensions of the labels.
        var xlabel_width = this.vis
            .select(".y_axis")
            .node()
            .getBoundingClientRect().width;
        if (this.padding.left < this.padding.left_original + xlabel_width) {
            this.padding.left = this.padding.left_original + xlabel_width;
            this.render(this.plot_div);
        }
    }

    get_plot_sizes() {
        this.h = this.row_height * this.metrics.length;
        var menu_spacing = 40;
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + menu_spacing + "px",
        });
    }

    setDefaults() {
        let score_ids = _.chain(this.data.aggregation.studies[0].data.rob_response_values)
            .filter(d => !NR_KEYS.includes(d))
            .reverse()
            .value();

        _.extend(this, {
            firstPass: true,
            included_metrics: [],
            padding: {},
            x_axis_settings: {
                domain: [0, 1],
                scale_type: "linear",
                text_orient: "bottom",
                axis_class: "axis x_axis",
                gridlines: true,
                gridline_class: "primary_gridlines x_gridlines",
                axis_labels: true,
                label_format: d3.format(".0%"),
            },
            y_axis_settings: {
                scale_type: "ordinal",
                text_orient: "left",
                axis_class: "axis y_axis",
                gridlines: true,
                gridline_class: "primary_gridlines x_gridlines",
                axis_labels: true,
                label_format: undefined,
            },
            score_ids,
            color_scale: d3.scale.ordinal().range(score_ids.map(d => SCORE_SHADES[d])),
        });
    }

    processData() {
        var included_metrics = this.data.settings.included_metrics,
            stack_order = this.score_ids,
            metrics,
            stack,
            dataset;

        dataset = _.chain(this.data.aggregation.metrics_dataset)
            .filter(d => _.includes(included_metrics, d.rob_scores[0].data.metric.id))
            .map(d => {
                // Filter to ONLY show default scores, not overrides:
                //   this may need to be a user-configurable option at some point
                let scores = d.rob_scores.filter(score => score.data.is_default === true),
                    weights = {},
                    total_weight = 1 / scores.length;

                this.score_ids.forEach(id => (weights[id] = 0));

                scores.forEach(function(rob) {
                    weights[rob.data.score] = (weights[rob.data.score] || 0) + total_weight;
                });

                // TODO - remove hard-coding of these values and use lookup
                if (_.has(weights, 15)) {
                    weights[15] = (weights[15] || 0) + (weights[12] || 0);
                    delete weights[12];
                } else if (_.has(weights, 25)) {
                    weights[25] = (weights[25] || 0) + (weights[22] || 0);
                    delete weights[22];
                } else {
                    throw "Unknown `-` value";
                }

                return _.extend(weights, {label: scores[0].data.metric.name});
            })
            .value();

        metrics = _.chain(dataset)
            .map(d => d.label)
            .uniq()
            .value();

        stack = d3.layout.stack()(
            _.map(stack_order, function(score) {
                return _.map(dataset, function(d) {
                    return {x: d.label, y: d[score]};
                });
            })
        );

        if (this.firstPass) {
            _.extend(this.padding, {
                top: this.data.settings.padding_top,
                right: this.data.settings.padding_right,
                bottom: this.data.settings.padding_bottom,
                left: this.data.settings.padding_left,
                left_original: this.data.settings.padding_left,
            });
            this.firstPass = false;
        }

        _.extend(this, {
            w: this.data.settings.plot_width,
            row_height: this.data.settings.row_height,
            dataset,
            metrics,
            stack_order,
            stack,
            title_str: this.data.settings.title,
            x_label_text: this.data.settings.xAxisLabel,
            y_label_text: this.data.settings.yAxisLabel,
        });
    }

    add_axes() {
        _.extend(this.x_axis_settings, {
            rangeRound: [0, this.w],
            number_ticks: 5,
            x_translate: 0,
            y_translate: this.h,
        });

        _.extend(this.y_axis_settings, {
            domain: this.metrics,
            number_ticks: this.metrics.length,
            rangeRound: [0, this.h],
            x_translate: 0,
            y_translate: 0,
        });

        this.build_y_axis();
        this.build_x_axis();
    }

    draw_visualizations() {
        var x = this.x_scale,
            y = this.y_scale,
            colors = this.color_scale,
            fmt = d3.format("%"),
            groups;

        this.bar_group = this.vis.append("g");

        // Add a group for each score.
        groups = this.vis
            .selectAll("g.score")
            .data(this.stack)
            .enter()
            .append("svg:g")
            .attr("class", "score")
            .style("fill", (d, i) => colors(i))
            .style("stroke", (d, i) => d3.rgb(colors(i)).darker());

        // Add a rect for each score.
        groups
            .selectAll("rect")
            .data(Object)
            .enter()
            .append("svg:rect")
            .attr("x", d => x(d.y0))
            .attr("y", d => y(d.x) + 5)
            .attr("width", d => x(d.y))
            .attr("height", 20);

        if (this.data.settings.show_values) {
            groups
                .selectAll("text")
                .data(Object)
                .enter()
                .append("text")
                .attr("class", "centeredLabel")
                .style("fill", "#555")
                .attr("x", d => x(d.y0) + x(d.y) / 2)
                .attr("y", d => y(d.x) + 20)
                .text(d => (d.y > 0 ? fmt(d.y) : ""));
        }
    }

    build_labels() {
        var svg = d3.select(this.svg),
            x,
            y;

        x = parseInt(this.svg.getBoundingClientRect().width / 2, 10);
        y = 25;
        svg.append("svg:text")
            .attr("x", x)
            .attr("y", y)
            .text(this.title_str)
            .attr("text-anchor", "middle")
            .attr("class", "dr_title");

        x = this.w / 2;
        y = this.h + 30;
        this.vis
            .append("svg:text")
            .attr("x", x)
            .attr("y", y)
            .attr("text-anchor", "middle")
            .attr("class", "dr_axis_labels x_axis_label")
            .text(this.x_label_text);

        x = -this.padding.left + 15;
        y = this.h / 2;
        this.vis
            .append("svg:text")
            .attr("x", x)
            .attr("y", y)
            .attr("text-anchor", "middle")
            .attr("transform", "rotate(270, {0}, {1})".printf(x, y))
            .attr("class", "dr_axis_labels x_axis_label")
            .text(this.y_label_text);
    }

    build_legend() {
        if (this.legend || !this.data.settings.show_legend) return;
        let rob_response_values = this.data.aggregation.studies[0].data.rob_response_values,
            options = {
                dev: this.options.dev || false,
                collapseNR: true,
            };
        this.legend = new RoBLegend(this.svg, this.data.settings, rob_response_values, [], options);
    }
}

export default RoBBarchartPlot;
