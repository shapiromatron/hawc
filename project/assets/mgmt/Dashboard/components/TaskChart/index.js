import React, { Component, PropTypes } from 'react';
import d3 from 'd3';

import xAxis from 'robVisual/components/Graph/xAxis';
import yAxis from 'robVisual/components/Graph/yAxis';
import './TaskChart.css';


class TaskChart extends Component {

    formatData() {

    }

    makeXScale(data){
        let { min, max, width, padding } = data;
        return d3.scale.linear()
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
        return (<div>MyComponent</div>);
    }
}

TaskChart.propTypes = {
    tasks: PropTypes.array.isRequired,
};

export default TaskChart;
