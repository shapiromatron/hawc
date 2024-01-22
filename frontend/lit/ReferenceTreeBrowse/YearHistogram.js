import * as d3 from "d3";
import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Plot from "react-plotly.js";

// adapted from /lit/api/assessment/:id/reference-year-histogram/
const dataTemplate = {
        hovertemplate: "Year=%{x}<br>count=%{y}",
        marker: {
            color: "#003d7b",
        },
        x: [],
        name: "",
        orientation: "v",
        showlegend: false,
        xaxis: "x",
        yaxis: "y",
        type: "histogram",
    },
    layoutTemplate = {
        xaxis: {
            title: {
                text: "Year",
            },
        },
        yaxis: {
            title: {
                text: "# References",
            },
        },
        legend: {
            tracegroupgap: 0,
        },
        margin: {
            t: 30,
            l: 40,
            r: 10,
            b: 40,
        },
        barmode: "relative",
        bargap: 0.1,
        plot_bgcolor: "white",
        autosize: true,
    },
    config = {
        modeBarButtonsToRemove: [
            "zoom2d",
            "pan2d",
            "select2d",
            "lasso2d",
            "zoomIn2d",
            "zoomOut2d",
            "autoScale2d",
            "toggleSpikelines",
            "hoverClosestCartesian",
            "hoverCompareCartesian",
        ],
    };

class YearHistogram extends Component {
    render() {
        const {references, onFilter, yearFilter} = this.props,
            years = _.chain(references)
                .map(d => d.data.year)
                .compact()
                .value();

        if (years.length < 10) {
            return null;
        }

        let data = _.cloneDeep(dataTemplate),
            layout = _.cloneDeep(layoutTemplate);

        data.x = years;

        return (
            <Plot
                className="yearHistogram"
                data={[data]}
                layout={layout}
                config={config}
                useResizeHandler={true}
                style={{width: "100%", height: 180}}
                onClick={function (e, d) {
                    /*
                    Ideally, the click events could discern if a bar was clicked or the background
                    is clicked, but that data doesn't appear available. Therefore, we check to see
                    if the selected item is the same as the current filter, and if it is, we reset.
                    */
                    let times = [],
                        range;
                    e.points.map(point => {
                        let start =
                                point.fullData.xbins.start +
                                point.binNumber * point.fullData.xbins.size,
                            end = start + point.fullData.xbins.size;
                        times.push(Math.ceil(start), Math.floor(end));
                    });
                    range = d3.extent(times);
                    if (yearFilter && yearFilter.min == range[0]) {
                        onFilter(null);
                    } else {
                        onFilter({min: range[0], max: range[1]});
                    }
                }}
            />
        );
    }
}
YearHistogram.propTypes = {
    references: PropTypes.array,
    onFilter: PropTypes.func,
    yearFilter: PropTypes.object,
};

export default YearHistogram;
