import React, { Component, PropTypes } from 'react';
import d3 from 'd3';

import './LineChart.css';


class LineChart extends Component {

    componentWillMount() {
        let { xScale, yScale } = this.props;
        this.line = d3.svg.line()
            .interpolate('cardinal')
            .x((d) => { return xScale(d.x); })
            .y((d) => { return yScale(d.y); });
    }

    render() {
        return (
            <g className="lineChart">
                <path d={this.line(this.props.data)} />
            </g>
        );
    }
}

LineChart.propTypes = {
    xScale: PropTypes.func.isRequired,
    yScale: PropTypes.func.isRequired,
    data: PropTypes.arrayOf(
        PropTypes.shape({
            x: PropTypes.number.isRequired,
            y: PropTypes.number.isRequired,
        }).isRequired
    ).isRequired,
};

export default LineChart;
