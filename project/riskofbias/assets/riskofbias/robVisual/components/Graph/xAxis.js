import React, { Component } from 'react';
import PropTypes from 'prop-types';
import d3 from 'd3';

class xAxis extends Component {
    componentWillMount() {
        let { xScale } = this.props;
        this.xAxis = d3.svg
            .axis()
            .scale(xScale)
            .orient('bottom')
            .ticks(5);
    }

    componentDidMount() {
        this.renderAxis();
    }

    componentDidUpdate() {
        this.renderAxis();
    }

    getLabelElement(axisLabel) {
        let { padding } = this.props;
        return (
            <text
                className="xAxis label"
                textAnchor="beginning"
                x={padding[3] + 10}
                y={axisLabel.offset}
            >
                {axisLabel.label}
            </text>
        );
    }

    render() {
        let { transform, label, padding, renderScale } = this.props,
            axisLabel = renderScale
                ? { offset: padding[2] - 15, label }
                : { offset: 20, label: label.substr(0, label.indexOf(' ')) },
            labelElement = this.getLabelElement(axisLabel);
        return (
            <g
                ref="xAxis"
                className="x axis"
                transform={`translate(${transform[0]}, ${transform[1]})`}
            >
                {labelElement}
            </g>
        );
    }

    renderAxis() {
        let { min, max, width, padding, xScale, renderScale } = this.props;
        xScale
            .domain([min, max])
            .range([padding[3], width - padding[1] - padding[3]]);

        renderScale ? d3.select(this.refs.xAxis).call(this.xAxis) : null;
    }
}

xAxis.propTypes = {
    min: PropTypes.number.isRequired,
    max: PropTypes.number.isRequired,
    width: PropTypes.number.isRequired,
    padding: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    transform: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    label: PropTypes.string.isRequired,
    renderScale: PropTypes.bool.isRequired,
    xScale: PropTypes.func.isRequired,
};

export default xAxis;
