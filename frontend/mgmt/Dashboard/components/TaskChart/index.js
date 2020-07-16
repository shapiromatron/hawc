import _ from "lodash";
import React, {PureComponent} from "react";
import PropTypes from "prop-types";
import * as d3 from "d3";

import BarChart from "Graphing/BarChart";
import XAxis from "Graphing/Axes/xAxis";
import YAxis from "Graphing/Axes/yAxisLabeled";
import "./TaskChart.css";

import {STATUS} from "mgmt/TaskTable/constants";

class TaskChart extends PureComponent {
    constructor(props) {
        super(props);
        this.state = this.getAxisData();
    }

    componentDidUpdate(nextProps, nextState) {
        this.setState(this.getAxisData());
    }

    getAxisData() {
        const setData = this.formatData(),
            xData = this.getXAxisData(setData),
            yData = this.getYAxisData(setData),
            xScale = this.makeXScale(xData),
            yScale = this.makeYScale(yData);
        return {
            setData,
            xData: {...xData, xScale},
            yData: {...yData, yScale},
        };
    }

    getYAxisData(setData) {
        const {chartData} = this.props,
            values = setData.map(d => d.key);
        return {
            ...chartData,
            transform: chartData.yTransform,
            label: "",
            values,
        };
    }

    getXAxisData(setData) {
        const {chartData} = this.props,
            values = setData.map(d => d.values.count);
        return {
            ...chartData,
            transform: chartData.xTransform,
            label: "Tasks",
            min: 0,
            max: d3.max(values),
            values,
        };
    }

    makeYScale(data) {
        let {height, padding, values} = data;
        return d3
            .scaleOrdinal()
            .domain(values)
            .rangeRoundBands([padding.top, height - padding.bottom], 0.4);
    }

    makeXScale(data) {
        let {width, padding, max} = data;
        return d3
            .scaleLinear()
            .domain([0, max])
            .range([padding.left, width - padding.right - padding.left]);
    }

    formatData() {
        let {tasks} = this.props,
            data = _.map(STATUS, function(val, key) {
                let keyInt = parseInt(key);
                return {
                    key: key.toString(),
                    values: {
                        count: tasks.filter(d => d.status === keyInt).length,
                        label: val.type,
                    },
                };
            });
        return data;
    }

    renderTitle() {
        const chartData = this.props.chartData;

        if (!chartData.label) {
            return null;
        }

        return (
            <text className="task-chart-title" x={chartData.width * 0.5} y={chartData.padding.top}>
                {chartData.label}
            </text>
        );
    }

    render() {
        const svg = d3.select("svg"),
            {xData, yData, setData} = this.state,
            ticks = d => {
                let mapper = {
                    "10": "not started",
                    "20": "started",
                    "30": "completed",
                    "40": "abandoned",
                };
                return mapper[d];
            };
        return (
            <div>
                <svg width={this.props.chartData.width} height={this.props.chartData.height}>
                    {this.renderTitle()}
                    <XAxis {...xData} ticks={5} renderScale />
                    <BarChart
                        xScale={xData.xScale}
                        yScale={yData.yScale}
                        data={setData}
                        chartData={this.props.chartData}
                        svg={svg}
                    />
                    <YAxis {...yData} ticks={ticks} renderScale />
                </svg>
            </div>
        );
    }
}

TaskChart.propTypes = {
    label: PropTypes.string,
    tasks: PropTypes.array.isRequired,
    chartData: PropTypes.shape({
        height: PropTypes.number.isRequired,
        width: PropTypes.number.isRequired,
        padding: PropTypes.shape({
            top: PropTypes.number.isRequired,
            right: PropTypes.number.isRequired,
            bottom: PropTypes.number.isRequired,
            left: PropTypes.number.isRequired,
        }).isRequired,
        xTransform: PropTypes.array.isRequired,
        yTransform: PropTypes.array.isRequired,
        label: PropTypes.string,
    }).isRequired,
};

export default TaskChart;
