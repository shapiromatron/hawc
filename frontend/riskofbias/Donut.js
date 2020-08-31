import _ from "lodash";
import $ from "$";
import * as d3 from "d3";

import D3Plot from "utils/D3Plot";

import {
    getMultiScoreDisplaySettings,
    BIAS_DIRECTION_SIMPLE,
    BIAS_DIRECTION_VERBOSE,
} from "riskofbias/constants";

class Donut extends D3Plot {
    constructor(study, el) {
        super();
        this.plot_div = $(el);
        this.set_defaults();
        this.data = this.get_dataset_info(study);
        if (this.data === null) {
            // stop here if we have no data
            return;
        }
        this.build_plot();
        $("body").on("keydown", () => {
            if (event.ctrlKey || event.metaKey) {
                this.toggle_lock_view();
            }
        });
    }

    set_defaults() {
        this.w = 800;
        this.h = 400;
        this.radius_inner = 30;
        this.radius_middle = 150;
        this.radius_outer = 200;
        this.padding = {top: 10, right: 10, bottom: 10, left: 10};
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + "px",
        });
        this.rotated_label_start_padding = 3; // padding from the inner radius where the rotated domain labels should start
        this.rotated_label_end_padding = 2; // padding from the middle radius where the rotated domain labels should end
        this.viewlock = false;
    }

    build_plot() {
        this.plot_div.html("");
        this.build_plot_skeleton(false);
        this.draw_visualizations();
        this.customize_menu();
        this.trigger_resize();
    }

    customize_menu() {
        this.add_menu();
        this.add_menu_button({
            id: "lock_view",
            cls: "btn btn-mini",
            title: "Lock current view (shortcut: press ctrl to toggle)",
            text: "",
            icon: "icon-lock",
            on_click: () => this.toggle_lock_view(),
        });
    }

    toggle_lock_view() {
        this.plot_div.find("#lock_view").toggleClass("btn-info");
        this.viewlock = !this.viewlock;
    }

    get_dataset_info(study) {
        // exit early if we have no data
        if (study.final === undefined || study.final.length === 0) {
            return null;
        }

        var domain_donut_data = [],
            question_donut_data = [],
            scores = study.final.scores.filter(
                score => score.metric.domain.is_overall_confidence === false
            ),
            overallScores = study.final.scores.filter(
                score => score.metric.domain.is_overall_confidence
            ),
            scoresByDomain = _.chain(scores)
                .groupBy("metric.domain.id")
                .values()
                .value(),
            getDataForMetric = (numMetrics, scores) => {
                let data = getMultiScoreDisplaySettings(scores),
                    defaultScore = scores.filter(score => score.is_default)[0],
                    notes = defaultScore.notes;

                if (scores.length > 1) {
                    notes =
                        "<p><i>Multiple scores exist for this metric; showing notes from default score</i></p>" +
                        notes;
                }
                return {
                    weight: 1 / numMetrics,
                    score: defaultScore.score,
                    score_text: defaultScore.score_text,
                    direction_simple: BIAS_DIRECTION_SIMPLE[defaultScore.bias_direction],
                    direction_verbose: BIAS_DIRECTION_VERBOSE[defaultScore.bias_direction],
                    score_svg_style: data.svgStyle,
                    score_css_style: data.cssStyle,
                    score_text_color: defaultScore.score_text_color,
                    criterion: defaultScore.metric.name,
                    notes,
                    parent_name: defaultScore.metric.domain.name,
                };
            };

        scoresByDomain.forEach((domainScores, domainIndex) => {
            let firstScore = domainScores[0],
                scoresByMetric = _.chain(domainScores)
                    .groupBy("metric.id")
                    .values()
                    .value();

            domain_donut_data.push({
                weight: 1, // equally weighted
                domain: firstScore.metric.domain.name,
                idxOrder: domainIndex,
                self: firstScore,
            });

            scoresByMetric.forEach(metricScores => {
                question_donut_data.push(getDataForMetric(scoresByMetric.length, metricScores));
            });
        });

        return {
            title: study.data.short_citation,
            domain_donut_data,
            question_donut_data,
            overall_question_data:
                overallScores.length > 0 ? getDataForMetric(1, overallScores) : null,
        };
    }

    draw_visualizations() {
        var self = this,
            donut_center = `translate(200,${this.h / 2})`;

        // setup gradients
        let gradientData = _.chain([this.data.question_donut_data, this.data.overall_question_data])
            .flatten()
            .compact()
            .filter(d => d.score_svg_style.gradient !== undefined)
            .map(d => d.score_svg_style.gradient)
            .value()
            .join();

        if (gradientData) {
            this.vis.append("defs").html(gradientData);
        }

        if (this.data.overall_question_data !== null) {
            this.center_circle = this.vis
                .append("circle")
                .attr("cx", 0)
                .attr("cy", 0)
                .attr("r", this.radius_inner)
                .style("fill", this.data.overall_question_data.score_svg_style.fill)
                .attr("transform", donut_center)
                .on("mouseover", function() {
                    if (self.viewlock) return;
                    d3.select(this).classed("hovered", true);
                    $(":animated")
                        .promise()
                        .done(() => self.show_subset(self.data.overall_question_data));
                })
                .on("mouseout", function(v) {
                    if (self.viewlock) return;
                    d3.select(this).classed("hovered", false);
                    metric_arcs.classed("hovered", false);
                    domain_arcs.classed("hovered", false);
                    self.subset_div.fadeOut("500", () => self.clear_subset());
                });

            this.center_text = this.vis
                .append("svg:text")
                .attr("x", 0)
                .attr("y", 0)
                .attr("text-anchor", "end")
                .attr("class", "centeredLabel")
                .attr("transform", donut_center)
                .text(
                    this.data.overall_question_data.score_text +
                        " " +
                        this.data.overall_question_data.direction_simple
                );
        }

        // setup pie layout generator
        this.pie_layout = d3
            .pie()
            .sort(null)
            .value(d => d.weight);

        // setup arc helper functions
        var domain_arc = d3
                .arc()
                .innerRadius(this.radius_inner)
                .outerRadius(this.radius_outer),
            details_arc = d3
                .arc()
                .innerRadius(this.radius_middle)
                .outerRadius(this.radius_outer);

        this.domain_outer_radius = this.radius_outer;
        this.details_arc = details_arc;
        this.domain_arc = domain_arc;

        // setup groups
        this.detail_arc_group = this.vis.append("g").attr("transform", donut_center);

        this.detail_label_group = this.vis.append("g").attr("transform", donut_center);

        this.domain_arc_group = this.vis.append("g").attr("transform", donut_center);

        this.domain_label_group = this.vis.append("g").attr("transform", donut_center);

        // rotate the labels
        var labelArc = d3
            .arc()
            .innerRadius(this.radius_inner + this.rotated_label_start_padding)
            .outerRadius(this.radius_inner + this.rotated_label_start_padding);

        // add domain labels. Two sets because we want two rows of information
        this.domain_domain_labels = this.domain_label_group
            .selectAll("text1")
            .data(this.pie_layout(this.data.domain_donut_data))
            .enter()
            .append("text")
            .attr("alignment-baseline", "middle")
            .attr("text-anchor", d => (d.endAngle < Math.PI ? "start" : "end"))
            .attr("transform", d => {
                let pos = labelArc.centroid(d),
                    midAngle =
                        d.endAngle < Math.PI
                            ? d.startAngle / 2 + d.endAngle / 2
                            : d.startAngle / 2 + d.endAngle / 2 + Math.PI,
                    rotatedMidAngle = (midAngle * 180) / Math.PI;
                return `translate(${pos[0]},${pos[1]}) rotate(-90) rotate(${rotatedMidAngle})`;
            })
            .attr("pointer-events", "none")
            .classed("autosized", true)
            .text(d => d.data.domain);

        $(document).ready(() => self.autosize_domain_labels());

        // add metric labels
        this.detail_label_group
            .selectAll("text")
            .data(this.pie_layout(this.data.question_donut_data))
            .enter()
            .append("text")
            .attr("class", "centeredLabel")
            .style("fill", d => d.data.score_text_color)
            .attr("transform", d => `translate(${details_arc.centroid(d)})`)
            .attr("text-anchor", "middle")
            .text(d => d.data.score_text + " " + d.data.direction_simple);

        // add detail arcs
        let metric_arcs = this.detail_arc_group
            .selectAll("path")
            .data(this.pie_layout(this.data.question_donut_data))
            .enter()
            .append("path")
            .style("fill", d => d.data.score_svg_style.fill)
            .attr("class", "donuts metric_arc")
            .attr("d", details_arc)
            .on("mouseover", function(v1) {
                if (self.viewlock) return;
                d3.select(this).classed("hovered", true);
                $(":animated")
                    .promise()
                    .done(() => self.show_subset(v1.data));
            })
            .on("mouseout", function(v) {
                if (self.viewlock) return;
                d3.select(this).classed("hovered", false);
                metric_arcs.classed("hovered", false);
                domain_arcs.classed("hovered", false);
                self.subset_div.fadeOut("500", () => self.clear_subset());
            });

        // add domain arcs
        var domain_arcs = this.domain_arc_group
            .selectAll("path")
            .data(this.pie_layout(this.data.domain_donut_data))
            .enter()
            .append("path")
            .attr("class", "donuts domain_arc")
            .on("mouseover", function(domain) {
                if (self.viewlock) return;
                d3.select(this).classed("hovered", true);
                $(":animated")
                    .promise()
                    .done(() => self.show_domain_header(domain.data.domain));
            })
            .on("mouseout", function(v) {
                if (self.viewlock) return;
                d3.select(this).classed("hovered", false);
                metric_arcs.classed("hovered", false);
                domain_arcs.classed("hovered", false);
                self.subset_div.fadeOut("500", () => self.clear_subset());
            })
            .attr("d", domain_arc);
        this.domain_arcs = domain_arcs;

        // build plot div, but make hidden by default
        this.subset_div = $("<div></div>").css({
            position: "relative",
            display: "none",
            height: -this.h - this.padding.top - this.padding.bottom,
            padding: "5px",
            width: this.w / 2 - this.padding.left - this.padding.right,
            left: this.w / 2 + this.padding.left + this.padding.right + 10,
            top: -this.h + this.padding.top + 10,
        });
        this.plot_div.append(this.subset_div);

        // print title
        this.title = this.vis
            .append("svg:text")
            .attr("x", this.w)
            .attr("y", this.h)
            .attr("text-anchor", "end")
            .attr("class", "dr_title")
            .text(this.data.title);

        setTimeout(() => this.toggle_domain_width(), 2);
    }

    autosize_domain_labels() {
        // shrinks the rotated domain labels so that they fit within the defined radii. Easiest way to do this is to just
        // repeatedly try successively smaller labels and then check them against their bounding box.
        var maxLabelWidth =
            this.radius_middle -
            this.radius_inner -
            this.rotated_label_start_padding -
            this.rotated_label_end_padding;

        var autosizeFields = $("text.autosized");
        autosizeFields.each(function() {
            var fld = $(this);
            if (fld[0].getBBox().width > maxLabelWidth) {
                var choppedText = fld.html().slice(0, -3);
                while (choppedText.length > 0) {
                    var abbreviatedText = choppedText + "...";
                    fld.html(abbreviatedText);

                    // getBBox needs to be fetched after each content update
                    if (fld[0].getBBox().width <= maxLabelWidth) {
                        break;
                    } else {
                        choppedText = choppedText.slice(0, -1);
                    }
                }
            }
        });
    }

    toggle_domain_width() {
        var new_radius = this.radius_middle;
        if (this.domain_outer_radius === this.radius_middle) new_radius = this.radius_outer;

        this.domain_arc = d3
            .arc()
            .innerRadius(this.radius_inner)
            .outerRadius(new_radius);
        this.domain_outer_radius = new_radius;

        this.domain_arcs
            .transition()
            .duration("500")
            .attr("d", this.domain_arc);
    }

    clear_subset() {
        this.subset_div.empty();
    }

    show_subset(metric) {
        this.clear_subset();
        this.subset_div.append(`<h4>${metric.parent_name}</h4>`);
        var ol = $('<ol class="score-details"></ol>'),
            div = $("<div>")
                .text(metric.score_text + " " + metric.direction_simple)
                .attr("class", "scorebox")
                .css(metric.score_css_style),
            metric_txt = $("<b>").text(metric.criterion),
            direction_txt =
                metric.direction_verbose == "" ? null : $("<p>").html(metric.direction_verbose),
            notes_txt = $("<p>")
                .html(metric.notes)
                .css({height: 250, overflow: "auto"});
        ol.append($("<li>").html([div, metric_txt, direction_txt, notes_txt]));
        this.subset_div.append(ol);
        this.subset_div.fadeIn("500");
    }

    show_domain_header(domain) {
        this.clear_subset();
        this.subset_div.append(`<h4>${domain}</h4>`);
        this.subset_div.fadeIn("500");
    }
}

export default Donut;
