import React, { PureComponent, PropTypes } from 'react';
import d3 from 'd3';

import BarChart from 'Graphing/BarChart';
import XAxis from 'Graphing/Axes/xAxis';
import YAxis from 'Graphing/Axes/yAxisLabeled';
import './TaskChart.css';


class TaskChart extends PureComponent {

    componentWillMount() {
        this.setAxisData();
    }

    componentWillUpdate(nextProps, nextState) {
        this.setAxisData();
    }

    setAxisData() {
        const setData = this.formatData(),
            xData = this.getXAxisData(setData),
            yData = this.getYAxisData(setData),
            xScale = this.makeXScale(xData),
            yScale = this.makeYScale(yData);
        this.setState({
            setData,
            xData: { ...xData, xScale },
            yData: { ...yData, yScale },
        });
    }

    getYAxisData(setData) {
        const { chartData } = this.props,
            values = setData.map((d) => d.key);
        return {
            ...chartData,
            transform: chartData.yTransform,
            label: '',
            values,
        };
    }

    getXAxisData(setData) {
        const { chartData } = this.props,
            values = setData.map((d) => d.values.count);
        return {
            ...chartData,
            transform: chartData.xTransform,
            label: 'Tasks',
            min: 0,
            max: d3.max(values),
            values,
        };
    }

    makeYScale(data){
        let { height, padding, values } = data;
        return d3.scale.ordinal()
            .domain(values)
            .rangeRoundBands([padding.top, height - padding.bottom], 0.4);
    }


    makeXScale(data){
        let { width, padding, max } = data;
        return d3.scale.linear()
            .domain([0, max])
            .range([padding.left, width - padding.right - padding.left]);
    }


    formatData() {
        let { tasks } = this.props,
            data = d3.nest()
                .key((d) => d.status)
                .rollup((d) => { return { count: d.length, label: d[0].status_display }; })
                .entries(tasks);
        return data;
    }

    render() {
        const svg = d3.select('svg'),
            { xData, yData, setData } = this.state,
            ticks = (d) => {
                let mapper = {
                    '10': 'not started',
                    '20': 'started',
                    '30': 'completed',
                    '40': 'abandoned',
                };
                return mapper[d];
            };
        return (
            <div>
                <h4>Assessment-wide task completion</h4>
                <svg width={this.props.chartData.width} height={this.props.chartData.height}>
                    <XAxis {...xData} ticks={5} renderScale/>
                    <BarChart xScale={xData.xScale} yScale={yData.yScale} data={setData} chartData={this.props.chartData} svg={svg}/>
                    <YAxis {...yData} ticks={ticks} renderScale/>
                </svg>
            </div>
        );
    }
}

TaskChart.propTypes = {
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
    }).isRequired,
};

export default TaskChart;
