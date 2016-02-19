import React, { Component } from 'react';

export default class yAxis extends Component {
    componentWillMount() {
        this.yScale = d3.scale.linear();
        this.yAxis = d3.svg.axis()
            .scale(this.yScale)
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
        let { transform, label } = this.props,
            labelElement = <text className='yAxis label' textAnchor='end' y='15'>{label}</text>;
        return (
            <g ref='yAxis' className='y axis'
            transform={`translate(${transform[0]}, ${transform[1]})`}>
                {labelElement}
            </g>
        );
    }

    renderAxis() {
        let { min, max, height, padding } = this.props;
        this.yScale
            .domain([max, min])
            .range([padding[0], height - padding[2]]);

        d3.select(this.refs.yAxis).call(this.yAxis);
    }
}
