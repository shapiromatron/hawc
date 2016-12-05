import React, { Component, PropTypes } from 'react';
import d3 from 'd3';
import _ from 'underscore';

import XAxis from 'Graphing/xAxis';
import YAxis from 'Graphing/yAxis';
import './TaskChart.css';


class TaskChart extends Component {

    componentWillMount() {
        const xData = this.getXAxisData(),
            yData = this.getYAxisData(),
            xScale = this.makeXScale(xData),
            yScale = this.makeYScale(yData);

        this.setState({
            xData: { ...xData, xScale},
            yData: { ...yData, yScale},
        });
    }


    formatData() {
        let { tasks } = this.props,
            parseDate = d3.time.format("%d-%b-%y").parse
        return tasks;
    }

    getXAxisData() {
        const { chartData, tasks } = this.props;
        return {
            ...chartData,
            transform: chartData.xTransform,
            label: 'Date',
            min: Date.parse(d3.min(_.compact(_.pluck(tasks, 'started')))),
            max: Date.now(),
        };
    }

    getYAxisData() {
        const { chartData, tasks } = this.props;
        return {
            ...chartData,
            transform: chartData.yTransform,
            label: 'Task completion',
            min: 0,
            max: tasks.length,
        };
    }

    makeXScale(data){
        let { min, max, width, padding } = data;
        return d3.time.scale()
            .domain([min, max])
            .range([padding[3], width - padding[1] - padding[3]]);
    }


    makeYScale(data){
        let { min, max, height, padding } = data;
        return d3.scale.linear()
            .domain([max, min])
            .range([padding[0], height - padding[2]]);
    }

    render() {
        let tasks = this.formatData();
        return (
            <svg>
                <XAxis {...this.state.xData} renderScale ticks={d3.time.days}/>

                <YAxis {...this.state.yData} renderScale/>
            </svg>
        );
    }
}

TaskChart.propTypes = {
    tasks: PropTypes.array.isRequired,
    chartData: PropTypes.shape({
        height: PropTypes.number.isRequired,
        width: PropTypes.number.isRequired,
        padding: PropTypes.array.isRequired,
        xTransform: PropTypes.array.isRequired,
        yTransform: PropTypes.array.isRequired
    }).isRequired,
};

export default TaskChart;
