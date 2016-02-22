import React, { Component, PropTypes } from 'react';


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

    render() {
        let { transform, label, padding, renderScale } = this.props,
            labelOffset = renderScale ? padding[3] - 20 : 20,
            labelElement = <text className='yAxis label' textAnchor='end' y={`-${labelOffset}`} x={0} transform={`rotate(-90)`}>{label}</text>;
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
            .range([padding[0], height - padding[2]]);

        renderScale ? d3.select(this.refs.yAxis).call(this.yAxis) : null;
    }
}

yAxis.propTypes = {
    min: PropTypes.number.isRequired,
    max: PropTypes.number.isRequired,
    height: PropTypes.number.isRequired,
    padding: PropTypes.arrayOf(
        PropTypes.number.isRequired
    ).isRequired,
    transform: PropTypes.arrayOf(
        PropTypes.number.isRequired
    ).isRequired,
    label: PropTypes.string.isRequired,
    renderScale: PropTypes.bool.isRequired,
    yScale: PropTypes.func.isRequired,
};

export default yAxis;
