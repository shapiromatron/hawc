import React, { Component } from 'react';
import PropTypes from 'prop-types';
import d3 from 'd3';
import _ from 'lodash';

import DoseAxis from './xAxis';
import ResponseAxis from './yAxis';
import SplineChart from './SplineChart';

class DoseResponseChart extends Component {
    componentWillMount() {
        let { doses, responses } = this.props,
            doseData = this.getDoseAxisData(),
            responseData = this.getResponseAxisData(),
            chartData = _.map(responses, (d, i) => {
                return {
                    x: doses[i].dose,
                    y: d.response,
                    significant: d.significant,
                };
            }),
            xScale = this.makeXScale(doseData),
            yScale = this.makeYScale(responseData);

        this.setState({
            doseData: { ...doseData, xScale },
            responseData: { ...responseData, yScale },
            chartData: { data: chartData, yScale, xScale },
        });
    }

    makeXScale(data) {
        let { min, max, width, padding } = data;
        return d3.scale
            .linear()
            .domain([min, max])
            .range([padding[3], width - padding[1] - padding[3]]);
    }

    makeYScale(data) {
        let { min, max, height, padding } = data;
        return d3.scale
            .linear()
            .domain([max, min])
            .range([padding[0], height - padding[2]]);
    }

    getDoseAxisData() {
        let { chartData, doses } = this.props;
        return {
            ...chartData,
            transform: chartData.xTransform,
            label: `Dose of ${doses[0].unit}`,
            min: _.min(_.map(doses, 'dose')),
            max: _.max(_.map(doses, 'dose')),
        };
    }

    getResponseAxisData() {
        let { chartData, responses } = this.props;
        return {
            ...chartData,
            transform: chartData.yTransform,
            label: `Response ${responses[0].unit}`,
            min: _.min(_.map(responses, 'response')),
            max: _.max(_.map(responses, 'response')),
        };
    }

    render() {
        let { width, height, radius } = this.props.chartData;
        return (
            <svg width={width} height={height}>
                <DoseAxis {...this.state.doseData} renderScale={false} />
                <SplineChart {...this.state.chartData} radius={radius} />
                <ResponseAxis
                    {...this.state.responseData}
                    renderScale={false}
                />
            </svg>
        );
    }
}

DoseResponseChart.propTypes = {
    chartData: PropTypes.shape({
        width: PropTypes.number.isRequired,
        height: PropTypes.number.isRequired,
        radius: PropTypes.number.isRequired,
        padding: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
        xTransform: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
        yTransform: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    }),
};

export default DoseResponseChart;
