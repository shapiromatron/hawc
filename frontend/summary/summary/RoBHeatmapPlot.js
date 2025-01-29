import * as d3 from "d3";
import _ from "lodash";
import {
    BIAS_DIRECTION_COMPACT,
    BIAS_DIRECTION_DOWN,
    BIAS_DIRECTION_UP,
    FOOTNOTES,
    getMultiScoreDisplaySettings,
} from "riskofbias/constants";
import RiskOfBiasScore from "riskofbias/RiskOfBiasScore";
import {renderCrossStudyDisplay} from "riskofbias/robTable/components/CrossStudyDisplay";
import {renderRiskOfBiasDisplay} from "riskofbias/robTable/components/RiskOfBiasDisplay";
import HAWCModal from "shared/utils/HAWCModal";
import HAWCUtils from "shared/utils/HAWCUtils";

import $ from "$";

import D3Visualization from "./D3Visualization";
import RoBLegend from "./RoBLegend";

class RoBHeatmapPlot extends D3Visualization {
    constructor(parent, data, options) {
        // heatmap of rob information. Criteria are on the y-axis,
        // and studies are on the x-axis
        super(...arguments);
        this.setDefaults();
        this.modal = new HAWCModal();
    }

    render($div) {
        this.plot_div = $div.html("");
        this.processData();
        if (this.cells_data.length === 0) {
            let robName = this.data.assessment_rob_name.toLowerCase();
            return HAWCUtils.addAlert(
                `Error: no studies with ${robName} selected. Please select at least one study with ${robName}.`,
                this.plot_div
            );
        }
        this.get_plot_sizes();
        this.build_plot_skeleton(false, "A heatmap visualization of judgments for each study");
        this.add_axes();
        this.draw_visualization();
        this.resize_plot_dimensions();
        this.add_menu();
        this.build_labels();
        this.build_legend();
        this.trigger_resize();
    }

    get_plot_sizes() {
        this.w = this.cell_size * this.xVals.length;
        this.h = this.cell_size * this.yVals.length;
        var menu_spacing = 40;
        this.plot_div.css({
            height: this.h + this.padding.top + this.padding.bottom + menu_spacing + "px",
        });
    }

    setDefaults() {
        _.extend(this, {
            firstPass: true,
            included_metrics: [],
            padding: {},
            x_axis_settings: {
                scale_type: "ordinal",
                text_orient: "top",
                axis_class: "axis x_axis",
                gridlines: true,
                gridline_class: "primary_gridlines x_gridlines",
                axis_labels: true,
                label_format: undefined, //default
            },
            y_axis_settings: {
                scale_type: "ordinal",
                text_orient: "left",
                axis_class: "axis y_axis",
                gridlines: true,
                gridline_class: "primary_gridlines x_gridlines",
                axis_labels: true,
                label_format: undefined, //default
            },
        });
    }

    processData() {
        var cells_data = [],
            gradients_data = [],
            excluded_score_ids = new Set(this.data.settings.excluded_score_ids),
            included_metrics = this.data.settings.included_metrics,
            studies,
            metrics,
            xIsStudy,
            study_label_field = this.data.settings.study_label_field
                ? this.data.settings.study_label_field
                : "short_citation"; // use `short_citation` for backwards compatible default

        _.each(this.data.aggregation.metrics_dataset, function(metric) {
            _.chain(metric.rob_scores)
                .filter(rob => _.includes(included_metrics, rob.data.metric.id))
                .groupBy(rob => rob.study.data.id)
                .values()
                .each(robArray => {
                    const displayedScores = robArray.filter(
                        rob => !excluded_score_ids.has(rob.data.id)
                    );
                    if (displayedScores.length === 0) {
                        return;
                    }
                    const displayData = getMultiScoreDisplaySettings(
                            displayedScores.map(rob => rob.data)
                        ),
                        metric_name =
                            displayedScores[0].data.metric.use_short_name === true &&
                            displayedScores[0].data.metric.short_name !== ""
                                ? displayedScores[0].data.metric.short_name
                                : displayedScores[0].data.metric.name;
                    if (displayData.svgStyle.gradient) {
                        gradients_data.push(displayData.svgStyle.gradient);
                    }
                    cells_data.push({
                        robArray,
                        directions: displayData.directions,
                        metric: displayedScores[0].data.metric,
                        metric_label: metric_name,
                        score_color: displayData.svgStyle.fill,
                        score_text: displayData.symbolShortText,
                        score_text_color: displayedScores[0].data.score_text_color,
                        study: displayedScores[0].study,
                        study_label: displayedScores[0].study.data[study_label_field],
                        symbols: displayData.symbols,
                    });
                })
                .value();
        });

        // default sort order alphabetically
        studies = _.chain(cells_data)
            .map(d => d.study_label)
            .uniq()
            .sort()
            .value();
        if (this.data.settings.sort_order === "overall_confidence") {
            // attempt to sort by overall confidence, but only if values are found
            const tmp = _.chain(cells_data)
                .filter(d => d.robArray[0].data.metric.domain.is_overall_confidence)
                .map(d => {
                    return {
                        study_label: d.study_label,
                        score: _.meanBy(d.robArray, f => f.data.score),
                    };
                })
                .orderBy(["score", "study_label"], ["desc", "asc"])
                .map(d => d.study_label)
                .uniq()
                .value();
            if (tmp.length > 0) {
                studies = tmp;
            }
        }

        metrics = _.chain(cells_data)
            .map(d => d.metric_label)
            .uniq()
            .value();

        if (this.firstPass) {
            _.extend(this.padding, {
                top: this.data.settings.padding_top,
                right: this.data.settings.padding_right,
                bottom: this.data.settings.padding_bottom,
                left: this.data.settings.padding_left,
                top_original: this.data.settings.padding_top,
                right_original: this.data.settings.padding_right,
                left_original: this.data.settings.padding_left,
            });
            this.firstPass = false;
        }

        xIsStudy = this.data.settings.x_field !== "metric";
        _.extend(this, {
            cell_size: this.data.settings.cell_size,
            cells_data,
            has_multiple_scores: cells_data.filter(d => d.symbols.length > 1).length > 0,
            cells_data_up: cells_data.filter(d => _.includes(d.directions, BIAS_DIRECTION_UP)),
            cells_data_down: cells_data.filter(d => _.includes(d.directions, BIAS_DIRECTION_DOWN)),
            gradients_data,
            studies,
            metrics,
            title_str: this.data.settings.title,
            x_label_text: this.data.settings.xAxisLabel,
            y_label_text: this.data.settings.yAxisLabel,
            xIsStudy,
            xVals: xIsStudy ? studies : metrics,
            yVals: !xIsStudy ? studies : metrics,
            xField: xIsStudy ? "study_label" : "metric_label",
            yField: !xIsStudy ? "study_label" : "metric_label",
        });
    }

    add_axes() {
        _.extend(this.x_axis_settings, {
            domain: this.xVals,
            rangeRound: [0, this.w],
            number_ticks: this.xVals.length,
            x_translate: 0,
            y_translate: 0,
        });

        _.extend(this.y_axis_settings, {
            domain: this.yVals,
            rangeRound: [0, this.h],
            number_ticks: this.yVals.length,
            x_translate: 0,
            y_translate: 0,
        });

        this.build_y_axis();
        this.build_x_axis();

        d3.select(this.svg)
            .selectAll(".x_axis text")
            .style("text-anchor", "start")
            .attr("dx", "5px")
            .attr("dy", "0px")
            .attr("transform", "rotate(-25)");
    }

    draw_visualization() {
        var self = this,
            x = this.x_scale,
            y = this.y_scale,
            width = this.cell_size,
            half_width = width / 2,
            quarter_width = width * 0.25,
            three_quarter_width = width * 0.75,
            robName = this.data.assessment_rob_name,
            showSQs = function(v) {
                self.print_details(self.modal.getBody(), $(this).data("robs"));
                self.modal
                    .addHeader(`<h4>${robName}: ${this.textContent}</h4>`)
                    .addFooter("")
                    .show({maxWidth: 900});
            },
            getMetricSQs = function(i, v) {
                $(this).data("robs", {
                    type: "metric",
                    robs: self.cells_data
                        .filter(cell => cell.metric_label === v.textContent)
                        .map(cell => cell.robArray),
                });
            },
            getStudySQs = function(i, v) {
                $(this).data("robs", {
                    type: "study",
                    robs: self.cells_data
                        .filter(cell => cell.study_label === v.textContent)
                        .map(cell => cell.robArray),
                });
            },
            hideHovers = function() {
                self.draw_hovers(this, {draw: false});
            };

        if (this.gradients_data.length > 0) {
            this.vis.append("defs").html(this.gradients_data.join());
        }

        this.cells_group = this.vis.append("g");

        this.cells = this.cells_group
            .selectAll("svg.rect")
            .data(this.cells_data)
            .enter()
            .append("rect")
            .attr("x", d => x(d[self.xField]))
            .attr("y", d => y(d[self.yField]))
            .attr("height", width)
            .attr("width", width)
            .attr("class", d =>
                d.metric.domain.is_overall_confidence
                    ? "heatmap_selectable_bold"
                    : "heatmap_selectable"
            )
            .style("fill", d => d.score_color)
            .on("mouseover", (event, v) => this.draw_hovers(v, {draw: true, type: "cell"}))
            .on("mouseout", (event, v) => this.draw_hovers(v, {draw: false}))
            .on("click", (event, v) => {
                this.print_details(this.modal.getBody(), {
                    type: "cell",
                    robs: v.robArray,
                });
                this.modal
                    .addHeader(`<h4>${robName}</h4>`)
                    .addFooter("")
                    .show({maxWidth: 900});
            });

        this.score = this.cells_group
            .selectAll("svg.text")
            .data(this.cells_data)
            .enter()
            .append("text")
            .attr("x", d => x(d[self.xField]) + half_width)
            .attr("y", d => y(d[self.yField]) + half_width)
            .attr("text-anchor", "middle")
            .attr("dy", "3.5px")
            .attr("class", function(d) {
                var returnValue = "centeredLabel";

                if (
                    typeof self.data != "undefined" &&
                    typeof self.data.aggregation != "undefined" &&
                    typeof self.data.aggregation.metrics_dataset != "undefined" &&
                    d < self.data.aggregation.metrics_dataset.length &&
                    typeof self.data.aggregation.metrics_dataset[d].domain_is_overall_confidence ==
                        "boolean" &&
                    self.data.aggregation.metrics_dataset[d].domain_is_overall_confidence
                ) {
                    returnValue = "heatmap_selectable_bold";
                }

                return returnValue;
            })
            .style("fill", d => d.score_text_color)
            .text(d => d.score_text);

        this.direction_up = this.cells_group
            .selectAll("svg.text")
            .data(this.cells_data_up)
            .enter()
            .append("text")
            .attr("x", d => x(d[self.xField]) + half_width)
            .attr("y", d => y(d[self.yField]) + quarter_width)
            .attr("text-anchor", "middle")
            .attr("class", d =>
                d.metric.domain.is_overall_confidence ? "heatmap_selectable_bold" : "centeredLabel"
            )
            .style("font-size", "10px")
            .style("fill", d => d.score_text_color)
            .text(BIAS_DIRECTION_COMPACT[BIAS_DIRECTION_UP]);

        this.direction_down = this.cells_group
            .selectAll("svg.text")
            .data(this.cells_data_down)
            .enter()
            .append("text")
            .attr("x", d => x(d[self.xField]) + half_width)
            .attr("y", d => y(d[self.yField]) + three_quarter_width)
            .attr("dy", "3.5px")
            .attr("text-anchor", "middle")
            .attr("class", d =>
                d.metric.domain.is_overall_confidence ? "heatmap_selectable_bold" : "centeredLabel"
            )
            .style("font-size", "10px")
            .style("fill", d => d.score_text_color)
            .text(BIAS_DIRECTION_COMPACT[BIAS_DIRECTION_DOWN]);

        $(".x_axis text")
            .each(this.xIsStudy ? getStudySQs : getMetricSQs)
            .attr("class", "heatmap_selectable")
            .on("mouseover", v => self.draw_hovers(v.target, {draw: true, type: "column"}))
            .on("mouseout", hideHovers)
            .on("click", showSQs);

        $(".y_axis text")
            .each(!this.xIsStudy ? getStudySQs : getMetricSQs)
            .attr("class", "heatmap_selectable")
            .on("mouseover", v => self.draw_hovers(v.target, {draw: true, type: "row"}))
            .on("mouseout", hideHovers)
            .on("click", showSQs);

        this.hover_group = this.vis.append("g");
    }

    resize_plot_dimensions() {
        /*
        Resize plot based on the dimensions of the labels.
        - top padding is padding specified by user + the x-axis label height
        - left padding is padding specified by user + the y-axis label width
        - right padding is the padding specified by the user,
            or the width of the label overhang over the heatmap,
            whichever is greater
        - (no change to bottom padding; whatever user specifies is used)
        */
        const xlabel_height = Math.ceil(
                this.vis
                    .select(".x_axis")
                    .node()
                    .getBoundingClientRect().height
            ),
            xlabel_width = Math.ceil(
                this.vis
                    .select(".x_axis")
                    .node()
                    .getBoundingClientRect().width
            ),
            ylabel_width = Math.ceil(
                this.vis
                    .select(".y_axis")
                    .node()
                    .getBoundingClientRect().width
            ),
            xlabel_overhang = xlabel_width - this.w + 5,
            top = xlabel_height + this.padding.top_original,
            left = ylabel_width + this.padding.left_original,
            right = Math.max(this.padding.right_original, xlabel_overhang);

        if (this.padding.top < top || this.padding.left < left || this.padding.right < right) {
            this.padding.top = top;
            this.padding.left = left;
            this.padding.right = right;
            this.render(this.plot_div);
        }
    }

    draw_hovers(v, options) {
        if (this.hover_study_bar) {
            this.hover_study_bar.remove();
        }

        if (!options.draw) {
            return;
        }

        var draw_type;
        switch (options.type) {
            case "cell":
                draw_type = {
                    x: this.x_scale(v[this.xField]),
                    y: this.y_scale(v[this.yField]),
                    height: this.cell_size,
                    width: this.cell_size,
                };
                break;
            case "row":
                draw_type = {
                    x: 0,
                    y: this.y_scale(v.textContent),
                    height: this.cell_size,
                    width: this.w,
                };
                break;
            case "column":
                draw_type = {
                    x: this.x_scale(v.textContent),
                    y: 0,
                    height: this.h,
                    width: this.cell_size,
                };
                break;
        }
        this.hover_study_bar = this.hover_group
            .selectAll("svg.rect")
            .data([draw_type])
            .enter()
            .append("rect")
            .attr("x", d => d.x)
            .attr("y", d => d.y)
            .attr("height", d => d.height)
            .attr("width", d => d.width)
            .attr("class", "heatmap_hovered");
    }

    build_labels() {
        var svg = d3.select(this.svg),
            visMidX = parseInt(this.svg.getBoundingClientRect().width / 2, 10),
            visMidY = parseInt(this.svg.getBoundingClientRect().height / 2, 10),
            midX = d3.mean(this.x_scale.range()),
            midY = d3.mean(this.y_scale.range());

        if ($(this.svg).find(".figureTitle").length === 0) {
            svg.append("svg:text")
                .attr("x", visMidX)
                .attr("y", 25)
                .text(this.title_str)
                .attr("text-anchor", "middle")
                .attr("class", "dr_title figureTitle");
        }

        var xLoc = this.padding.left + midX + 20,
            yLoc = visMidY * 2 - 5;

        svg.append("svg:text")
            .attr("x", xLoc)
            .attr("y", yLoc)
            .text(this.x_label_text)
            .attr("text-anchor", "middle")
            .attr("class", "dr_axis_labels x_axis_label");

        yLoc = this.padding.top + midY;

        svg.append("svg:text")
            .attr("x", 15)
            .attr("y", yLoc)
            .attr("transform", `rotate(270, 15, ${yLoc})`)
            .text(this.y_label_text)
            .attr("text-anchor", "middle")
            .attr("class", "dr_axis_labels y_axis_label");
    }

    build_legend() {
        if (this.legend || !this.data.settings.show_legend) {
            return;
        }
        const offset = parseInt(this.cell_size / 3),
            rowWidths = this.x_scale.domain().length * this.cell_size,
            options = {
                dev: this.options.dev || false,
                handleLegendDrag: this.options.handleLegendDrag,
                collapseNR: false,
                default_x: this.padding.left + rowWidths + offset,
                default_y: this.padding.top + offset,
            },
            getFootnoteOptions = () => {
                let footnotes = [];
                if (this.has_multiple_scores) {
                    footnotes.push(FOOTNOTES.MULTIPLE_SCORES);
                }
                if (this.cells_data_up.length > 0) {
                    footnotes.push(FOOTNOTES.BIAS_AWAY_NULL);
                }
                if (this.cells_data_down.length > 0) {
                    footnotes.push(FOOTNOTES.BIAS_TOWARDS_NULL);
                }
                return footnotes;
            },
            footnotes = getFootnoteOptions();

        this.legend = new RoBLegend(this.svg, this.data, footnotes, options);
    }

    print_details($div, d) {
        // delay rendering until modal is displayed, as component depends on accurate width.
        window.setTimeout(function() {
            switch (d.type) {
                case "cell":
                    renderRiskOfBiasDisplay(
                        RiskOfBiasScore.format_for_react(d.robs, {
                            display: "final",
                            isForm: false,
                            showStudyHeader: true,
                            studyUrl: d.robs[0].study.data.url,
                            studyName: d.robs[0].study.data.short_citation,
                        }),
                        $div[0]
                    );
                    break;
                case "study":
                    renderRiskOfBiasDisplay(
                        RiskOfBiasScore.format_for_react(_.flatten(d.robs), {
                            display: "final",
                            isForm: false,
                            showStudyHeader: true,
                            studyUrl: d.robs[0][0].study.data.url,
                            studyName: d.robs[0][0].study.data.short_citation,
                        }),
                        $div[0]
                    );
                    break;
                case "metric":
                    renderCrossStudyDisplay(
                        _.chain(d.robs)
                            .flatten()
                            .map(rob => {
                                rob.data.study = rob.study.data;
                                return rob.data;
                            })
                            .value(),
                        $div[0]
                    );
                    break;
            }
        }, 200);
    }
}

export default RoBHeatmapPlot;
