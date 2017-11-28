import React, { Component } from 'react';
import PropTypes from 'prop-types';
import d3 from 'd3';


class yAxis extends Component {

    componentWillMount() {
        let { yScale } = this.props;
        this.yAxis = d3.svg.axis()
            .scale(yScale)
            .orient('left')
            .ticks(5);
    }

    componentDidMount() {
        this.renderAxis();
    }

    componentDidUpdate() {
        this.renderAxis();
    }

    getLabelElement(axisLabel) {
        let { height, padding } = this.props;
        return <text
                className='yAxis label'
                textAnchor='beginning'
                y={`-${axisLabel.offset}`}
                x={padding.bottom - height}
                transform={`rotate(-90)`}>
                    {axisLabel.label}
            </text>;
    }

    render() {
        let { transform, label, padding, renderScale } = this.props,
            axisLabel = renderScale ?
                { offset: padding.left - 20, label} :
                { offset: 20, label: label.substr(0, label.indexOf(' '))},
            labelElement = this.getLabelElement(axisLabel);
        return (
            <g ref='yAxis' className='y axis'
            transform={`translate(${transform[0]}, ${transform[1]})`}>
                {labelElement}
            </g>
        );
    }

    renderAxis() {
        let { min, max, height, padding, yScale, renderScale } = this.props;
        yScale
            .domain([max, min])
            .range([padding.top, height - padding.bottom]);

        renderScale ? d3.select(this.refs.yAxis).call(this.yAxis) : null;
    }
}

yAxis.propTypes = {
    min: PropTypes.number.isRequired,
    max: PropTypes.number.isRequired,
    height: PropTypes.number.isRequired,
    padding: PropTypes.shape({
        top: PropTypes.number.isRequired,
        right: PropTypes.number.isRequired,
        bottom: PropTypes.number.isRequired,
        left: PropTypes.number.isRequired,
    }).isRequired,
    transform: PropTypes.arrayOf(
        PropTypes.number.isRequired
    ).isRequired,
    label: PropTypes.string.isRequired,
    renderScale: PropTypes.bool,
    yScale: PropTypes.func.isRequired,
};

export default yAxis;
