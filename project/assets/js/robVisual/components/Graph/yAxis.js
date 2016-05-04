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

    getLabelElement(axisLabel) {
        let { height, padding } = this.props;
        return <text
                className='yAxis label'
                textAnchor='beginning'
                y={`-${axisLabel.offset}`}
                x={ padding[2] - height}
                transform={`rotate(-90)`}>
                    {axisLabel.label}
            </text>;
    }

    render() {
        let { transform, label, padding, renderScale } = this.props,
            axisLabel = renderScale ?
                { offset: padding[3] - 20, label} :
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
    renderScale: PropTypes.bool,
    yScale: PropTypes.func.isRequired,
};

export default yAxis;
