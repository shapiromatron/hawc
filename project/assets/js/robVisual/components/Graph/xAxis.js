import React, { Component, PropTypes } from 'react';


class xAxis extends Component {
    componentWillMount() {
        let { xScale } = this.props;
        this.xAxis = d3.svg.axis()
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

    render() {
        let { transform, label, width, padding, renderScale } = this.props,
            labelOffset = renderScale ? padding[2] - 20 : 20,
            labelElement = <text className='xAxis label' textAnchor='middle' x={width/2} y={labelOffset} >{label}</text>;
        return (
            <g ref='xAxis' className="x axis"
                transform={`translate(${transform[0]}, ${transform[1]})`}>
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
    padding: PropTypes.arrayOf(
        PropTypes.number.isRequired
    ).isRequired,
    transform: PropTypes.arrayOf(
        PropTypes.number.isRequired
    ).isRequired,
    label: PropTypes.string.isRequired,
    renderScale: PropTypes.bool.isRequired,
    xScale: PropTypes.func.isRequired,
};

export default xAxis;
