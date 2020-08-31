import _ from "lodash";
import * as d3 from "d3";

import HAWCUtils from "utils/HAWCUtils";

import {
    NA_KEYS,
    NR_KEYS,
    SCORE_SHADES,
    SCORE_TEXT,
    SCORE_TEXT_DESCRIPTION_LEGEND,
    COLLAPSED_NR_FIELDS_DESCRIPTION,
} from "riskofbias/constants";

class RoBLegend {
    constructor(svg, settings, rob_response_values, footnotes, options) {
        this.svg = svg;
        this.settings = settings;
        this.rob_response_values = rob_response_values;
        this.footnotes = footnotes;
        this.options = options;
        this.render();
    }

    get_data() {
        let scores = _.intersectionBy(
                this.rob_response_values,
                _.keys(SCORE_TEXT_DESCRIPTION_LEGEND),
                parseInt
            ), // only display valid legend scores
            fields,
            collapseNR = this.options.collapseNR;

        // determine which scores to present in legend
        if (!this.settings.show_na_legend) {
            NA_KEYS.forEach(key => {
                if (scores.includes(key)) {
                    scores.splice(scores.indexOf(key), 1);
                }
            });
        }
        if (!this.settings.show_nr_legend || collapseNR) {
            NR_KEYS.forEach(key => {
                if (scores.includes(key)) {
                    scores.splice(scores.indexOf(key), 1);
                }
            });
        }
        fields = _.map(scores, function(v) {
            let desc = SCORE_TEXT_DESCRIPTION_LEGEND[v];
            if (collapseNR && COLLAPSED_NR_FIELDS_DESCRIPTION[v]) {
                desc = COLLAPSED_NR_FIELDS_DESCRIPTION[v];
            }
            return {
                value: v,
                color: SCORE_SHADES[v],
                text_color: String.contrasting_color(SCORE_SHADES[v]),
                text: SCORE_TEXT[v],
                description: desc,
            };
        });

        return fields;
    }

    render() {
        let svg = d3.select(this.svg),
            svgW = parseInt(svg.attr("width"), 10),
            svgH = parseInt(svg.attr("height"), 10),
            x = this.settings.legend_x,
            y = this.settings.legend_y,
            width = 22,
            half_width = width / 2,
            buff = 5,
            title_offset = 8,
            dim = this.svg.getBBox(),
            cursor = this.options.dev ? "pointer" : "auto",
            drag = this.options.dev
                ? HAWCUtils.updateDragLocationTransform((x, y) => {
                      this.settings.legend_x = parseInt(x, 10);
                      this.settings.legend_y = parseInt(y, 10);
                  })
                : function() {},
            fields = this.get_data(),
            title,
            g;

        // create a new g.legend_group object on the main svg graphic
        g = svg
            .append("g")
            .attr("transform", `translate(${x}, ${y})`)
            .attr("cursor", cursor)
            .call(drag);

        // add text 'Legend'; we set the x to a temporarily small value,
        // which we change below after we know the size of the legend
        title = g
            .append("text")
            .attr("x", 10)
            .attr("y", 8)
            .attr("text-anchor", "middle")
            .attr("class", "dr_title")
            .text("Legend");

        // Add color rectangles
        g.selectAll("svg.rect")
            .data(fields)
            .enter()
            .append("rect")
            .attr("x", 0)
            .attr("y", (d, i) => i * width + title_offset)
            .attr("height", width)
            .attr("width", width)
            .attr("class", "heatmap_selectable")
            .style("fill", d => d.color);

        // Add text label (++, --, etc.)
        g.selectAll("svg.text.labels")
            .data(fields)
            .enter()
            .append("text")
            .attr("x", half_width)
            .attr("y", (d, i) => i * width + half_width + title_offset)
            .attr("text-anchor", "middle")
            .attr("dy", "3.5px")
            .attr("class", "centeredLabel")
            .style("fill", d => d.text_color)
            .text(d => d.text);

        // Add text description
        g.selectAll("svg.text.desc")
            .data(fields)
            .enter()
            .append("text")
            .attr("x", width + 5)
            .attr("y", (d, i) => i * width + half_width + title_offset)
            .attr("dy", "3.5px")
            .attr("class", "dr_axis_labels")
            .text(d => d.description);

        // add footnotes
        if (this.footnotes.length > 0) {
            dim = g.node().getBBox();
            g.selectAll("svg.text.footnote_icon")
                .data(this.footnotes)
                .enter()
                .append("text")
                .attr("x", half_width)
                .attr("y", (d, i) => dim.height + (i + 1) * 15)
                .attr("class", "centeredLabel footnote_icon")
                .text(d => d[0]);

            g.selectAll("svg.text.footnote_text")
                .data(this.footnotes)
                .enter()
                .append("text")
                .attr("x", width + 5)
                .attr("y", (d, i) => dim.height + (i + 1) * 15)
                .attr("class", "dr_axis_labels footnote_text")
                .text(d => d[1]);
        }

        // add bounding-rectangle around legend
        dim = g.node().getBBox();
        g.insert("svg:rect", ":first-child")
            .attr("class", "legend")
            .attr("x", -buff)
            .attr("y", -buff)
            .attr("height", dim.height + 2 * buff)
            .attr("width", dim.width);

        // center the legend-text
        title.attr("x", dim.width / 2);

        // set legend in-bounds if out of svg boundaries
        if (x + dim.width > svgW) {
            x = svgW - dim.width - buff;
        }
        if (x < 0) {
            x = 2 * buff;
        }
        if (y + dim.height > svgH) {
            y = svgH - dim.height - 2 * buff;
        }
        if (y < 0) {
            y = 2 * buff;
        }
        g.attr("transform", `translate(${x},${y})`);
    }
}

export default RoBLegend;
