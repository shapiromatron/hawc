import _ from "lodash";
import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import Plot from "react-plotly.js";

import {STATUS} from "./constants";

const plotConfig = {
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
    },
    layoutBase = {
        title: "",
        titlefont: {fontweight: "bold"},
        margin: {l: 85, r: 0, t: 30, b: 30},
        width: 500,
        height: 200,
        xaxis: {title: "Tasks"},
        yaxis: {autorange: "reversed"},
    },
    dataBase = {
        type: "bar",
        textposition: "auto",
        hoverinfo: "none",
        orientation: "h",
    },
    formatData = tasks => {
        return _.chain(STATUS)
            .map((val, key) => {
                const keyInt = parseInt(key);
                return {
                    label: val.type,
                    color: val.color,
                    count: tasks.filter(d => d.status === keyInt).length,
                };
            })
            .value();
    };

@observer
class TaskChart extends Component {
    render() {
        const {label, tasks} = this.props,
            dataset = formatData(tasks),
            data = _.defaults(
                {
                    x: dataset.map(d => d.count),
                    y: dataset.map(d => d.label),
                    text: dataset.map(d => d.count.toString()),
                    marker: {color: dataset.map(d => d.color)},
                },
                dataBase
            ),
            layout = _.defaults({title: label}, layoutBase);
        return <Plot data={[data]} layout={layout} config={plotConfig} />;
    }
}
TaskChart.propTypes = {
    label: PropTypes.string.isRequired,
    tasks: PropTypes.array.isRequired,
};

export default TaskChart;
