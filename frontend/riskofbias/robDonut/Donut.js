import * as d3 from "d3";
import _ from "lodash";
import D3Plot from "shared/utils/D3Plot";
import h from "shared/utils/helpers";

import $ from "$";

import {
    BIAS_DIRECTION_SIMPLE,
    BIAS_DIRECTION_VERBOSE,
    getMultiScoreDisplaySettings,
} from "../constants";

class Donut extends D3Plot {
    render(store, el) {
        this.store = store;
        this.plot_div = $(el);
        this.set_defaults();
        this.data = this.get_dataset_info();
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
            position: "relative",
        });
        this.rotated_label_start_padding = 3; // padding from the inner radius where the rotated domain labels should start
        this.rotated_label_end_padding = 2; // padding from the middle radius where the rotated domain labels should end
        this.viewlock = false;
    }

    build_plot() {
        this.plot_div.html("");
        this.build_plot_skeleton(false, "A pie-chart of risk of bias/study evaluation metrics");
        this.customize_menu();
        this.draw_visualizations();
        this.trigger_resize();
        this.resize_subset();
    }

    customize_menu() {
        let old_toggle = this._toggle_menu_bar;
        this._toggle_menu_bar = () => {
            old_toggle.call(this);
            $(window).resize();
        };

        this.add_menu();
        this.add_menu_button({
            id: "lock_view",
            cls: "btn btn-sm",
            title: "Lock current view (shortcut: press ctrl to toggle)",
            text: "",
            icon: "fa fa-lock",
            on_click: () => this.toggle_lock_view(),
        });
    }

    toggle_lock_view() {
        this.plot_div.find("#lock_view").toggleClass("btn-info");
        this.viewlock = !this.viewlock;
    }

    get_dataset_info() {
        const {store} = this;
        var domain_donut_data = [],
            question_donut_data = [],
            scores = store.final.scores.filter(
                score => store.metricDomains[score.metric_id].is_overall_confidence === false
            ),
            overallScores = store.final.scores.filter(
                score => store.metricDomains[score.metric_id].is_overall_confidence
            ),
            scoresByDomain = _.chain(scores)
                .groupBy(s => store.metricDomains[s.metric_id].id)
                .values()
                .value(),
            getDataForMetric = (numMetrics, scores) => {
                let data = getMultiScoreDisplaySettings(scores),
                    defaultScore = scores.find(score => score.is_default) || scores[0],
                    notes = defaultScore.notes;

                if (scores.length > 1) {
                    notes =
                        "<p class='form-text my-1'><small><i>Multiple judgments exist for this metric; showing notes from the default judgment</small></i></p>" +
                        notes;
                }
                return {
                    weight: 1 / numMetrics,
                    score: defaultScore.score,
                    score_text: store.settings.score_metadata.symbols[defaultScore.score],
                    direction_simple: BIAS_DIRECTION_SIMPLE[defaultScore.bias_direction],
                    direction_verbose: BIAS_DIRECTION_VERBOSE[defaultScore.bias_direction],
                    score_svg_style: data.svgStyle,
                    score_css_style: data.cssStyle,
                    score_text_color: h.contrastingColor(
                        store.settings.score_metadata.colors[defaultScore.score]
                    ),
                    criterion: store.metrics[defaultScore.metric_id].name,
                    notes,
                    parent_name: store.metricDomains[defaultScore.metric_id].name,
                };
            };

        scoresByDomain.forEach((domainScores, domainIndex) => {
            let firstScore = domainScores[0],
                scoresByMetric = _.chain(domainScores).groupBy("metric_id").values().value();

            domain_donut_data.push({
                weight: 1, // equally weighted
                domain: store.metricDomains[firstScore.metric_id].name,
                idxOrder: domainIndex,
                self: firstScore,
            });

            scoresByMetric.forEach(metricScores => {
                question_donut_data.push(getDataForMetric(scoresByMetric.length, metricScores));
            });
        });

        return {
            title: store.study.short_citation,
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
                .on("mouseover", function () {
                    if (self.viewlock) return;
                    d3.select(this).classed("hovered", true);
                    $(":animated")
                        .promise()
                        .done(() => self.show_subset(self.data.overall_question_data));
                })
                .on("mouseout", function () {
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
        var domain_arc = d3.arc().innerRadius(this.radius_inner).outerRadius(this.radius_outer),
            details_arc = d3.arc().innerRadius(this.radius_middle).outerRadius(this.radius_outer);

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
            .on("mouseover", function (_event, v1) {
                if (self.viewlock) return;
                d3.select(this).classed("hovered", true);
                $(":animated")
                    .promise()
                    .done(() => self.show_subset(v1.data));
            })
            .on("mouseout", function () {
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
            .on("mouseover", function (_event, domain) {
                if (self.viewlock) return;
                d3.select(this).classed("hovered", true);
                $(":animated")
                    .promise()
                    .done(() => self.show_domain_header(domain.data.domain));
            })
            .on("mouseout", function () {
                if (self.viewlock) return;
                d3.select(this).classed("hovered", false);
                metric_arcs.classed("hovered", false);
                domain_arcs.classed("hovered", false);
                self.subset_div.fadeOut("500", () => self.clear_subset());
            })
            .attr("d", domain_arc);
        this.domain_arcs = domain_arcs;

        // build plot div, but make hidden by default
        this.subset_div = $("<div>").css({
            position: "absolute",
            display: "none",
            padding: "5px",
            overflow: "auto",
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

    resize_subset() {
        $(window).resize(() => {
            this.subset_div.css({
                height: this.svg.clientHeight - this.padding.top - this.padding.bottom,
                width: this.svg.clientWidth / 2 - this.padding.left - this.padding.right,
                left: this.svg.clientWidth / 2 + this.padding.left,
                top: this.padding.top,
            });
        });
        $(window).resize();
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
        autosizeFields.each(function () {
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

        this.domain_arc = d3.arc().innerRadius(this.radius_inner).outerRadius(new_radius);
        this.domain_outer_radius = new_radius;

        this.domain_arcs.transition().duration("500").attr("d", this.domain_arc);
    }

    clear_subset() {
        this.subset_div.empty();
    }

    show_subset(metric) {
        this.clear_subset();
        var card = $('<div class="card"></div>'),
            body = $('<div class="card-body"></div>'),
            title = $('<span class="card-title"></span>'),
            div = $("<div>")
                .text(metric.score_text + " " + metric.direction_simple)
                .attr("class", "scorebox")
                .css(metric.score_css_style),
            metric_txt = $("<b>").text(metric.criterion),
            direction_txt =
                metric.direction_verbose == ""
                    ? null
                    : $('<p class="card-text my-1">').html(metric.direction_verbose),
            notes_txt = $('<p class="card-text my-1">').html(metric.notes);
        body.append(title.html([div, metric_txt]));
        body.append(direction_txt, notes_txt);

        card.append(`<h4 class="card-header">${metric.parent_name}</h4>`);
        card.append(body);
        this.subset_div.append(card);
        this.subset_div.fadeIn("500");
    }

    show_domain_header(domain) {
        this.clear_subset();
        var card = $('<div class="card"></div>');
        card.append(`<h4 class="card-header">${domain}</h4>`);
        this.subset_div.append(card);
        this.subset_div.fadeIn("500");
    }
}

export default Donut;
