import React, { Component } from 'react';
import PropTypes from 'prop-types';
import d3 from 'd3';

import './LineChart.css';

class LineChart extends Component {
    componentWillMount() {
        let { xScale, yScale } = this.props;
        this.line = d3.svg
            .line()
            .interpolate('cardinal')
            .x((d) => {
                return xScale(d.x);
            })
            .y((d) => {
                return yScale(d.y);
            });
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
            significant: PropTypes.bool.isRequired,
        }).isRequired
    ).isRequired,
};

export default LineChart;
