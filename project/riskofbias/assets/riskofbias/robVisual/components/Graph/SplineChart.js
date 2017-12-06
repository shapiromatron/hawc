import React, { Component } from 'react';
import PropTypes from 'prop-types';
import d3 from 'd3';
import _ from 'lodash';

import './SplineChart.css';

class SplineChart extends Component {
    componentWillMount() {
        let { xScale, yScale, radius } = this.props;
        this.dot = d3.svg
            .symbol()
            .type('circle')
            .size(radius);
        this.line = d3.svg
            .line()
            .interpolate('cardinal')
            .x(d => {
                return xScale(d.x);
            })
            .y(d => {
                return yScale(d.y);
            });
    }

    render() {
        let { xScale, yScale, data } = this.props,
            circles = _.map(data, (d, i) => {
                let translate = `translate(${xScale(d.x)}, ${yScale(d.y)})`,
                    className = d.significant ? 'dot significant' : 'dot';
                return (
                    <path
                        key={`circle${i}`}
                        className={className}
                        d={this.dot()}
                        transform={translate}
                    />
                );
            });
        return (
            <g className="splineChart">
                <path className="line" d={this.line(this.props.data)} />
                {circles}
            </g>
        );
    }
}

SplineChart.propTypes = {
    data: PropTypes.arrayOf(
        PropTypes.shape({
            x: PropTypes.number.isRequired,
            y: PropTypes.number.isRequired,
            significant: PropTypes.bool.isRequired,
        })
    ).isRequired,
    xScale: PropTypes.func.isRequired,
    yScale: PropTypes.func.isRequired,
    radius: PropTypes.number.isRequired,
};

export default SplineChart;
