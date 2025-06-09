import * as d3 from "d3";
import _ from "lodash";
import {
    COLLAPSED_NR_FIELDS_DESCRIPTION,
    NA_KEYS,
    NR_KEYS,
    SCORE_SHADES,
    SCORE_TEXT,
    SCORE_TEXT_DESCRIPTION_LEGEND,
} from "riskofbias/constants";
import {DEFAULT} from "shared/constants";
import HAWCUtils from "shared/utils/HAWCUtils";
import h from "shared/utils/helpers";

class RoBLegend {
    constructor(svg, data, footnotes, options) {
        this.svg = svg;
        this.settings = data.settings;
        this.rob_settings = data.rob_settings;
        this.footnotes = footnotes;
        this.options = options;
        this.render();
    }

    get_data() {
        const {included_metrics, show_na_legend, show_nr_legend} = this.settings,
            {collapseNR} = this.options,
            includedItems = new Set(_.keys(SCORE_TEXT_DESCRIPTION_LEGEND).map(d => parseInt(d)));

        let response_values = _.chain(this.rob_settings.metrics)
            .filter(d => _.includes(included_metrics, d.id))
            .map(d => d.response_values)
            .flatten()
            .uniq()
            .filter(d => includedItems.has(d))
            .sort()
            .reverse()
            .value();

        if (show_na_legend == false) {
            response_values = _.pull(response_values, ...NA_KEYS);
        }

        if (show_nr_legend == false || collapseNR) {
            response_values = _.pull(response_values, ...NR_KEYS);
        }

        return response_values.map(score => {
            return {
                value: score,
                color: SCORE_SHADES[score],
                text_color: h.contrastingColor(SCORE_SHADES[score]),
                text: SCORE_TEXT[score],
                description:
                    collapseNR && COLLAPSED_NR_FIELDS_DESCRIPTION[score]
                        ? COLLAPSED_NR_FIELDS_DESCRIPTION[score]
                        : SCORE_TEXT_DESCRIPTION_LEGEND[score],
            };
        });
    }

    render() {
        const {legend_x, legend_y} = this.settings,
            {dev, default_x, default_y, handleLegendDrag} = this.options;

        let svg = d3.select(this.svg),
            svgW = parseInt(svg.attr("width"), 10),
            svgH = parseInt(svg.attr("height"), 10),
            x = legend_x === DEFAULT && default_x ? default_x : legend_x,
            y = legend_y === DEFAULT && default_y ? default_y : legend_y,
            width = 22,
            half_width = width / 2,
            buff = 5,
            title_offset = 8,
            dim = this.svg.getBBox(),
            cursor = dev ? "pointer" : "auto",
            drag = dev
                ? HAWCUtils.updateDragLocationTransform((x, y) =>
                      handleLegendDrag(parseInt(x), parseInt(y))
                  )
                : function () {},
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
            .attr("y", (_d, i) => i * width + title_offset)
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
            .attr("y", (_d, i) => i * width + half_width + title_offset)
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
            .attr("y", (_d, i) => i * width + half_width + title_offset)
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
                .attr("y", (_d, i) => dim.height + (i + 1) * 15)
                .attr("class", "centeredLabel footnote_icon")
                .text(d => d[0]);

            g.selectAll("svg.text.footnote_text")
                .data(this.footnotes)
                .enter()
                .append("text")
                .attr("x", width + 5)
                .attr("y", (_d, i) => dim.height + (i + 1) * 15)
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
