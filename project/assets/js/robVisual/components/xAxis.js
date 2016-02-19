import React, { Component } from 'react';

export default class xAxis extends Component {
    componentWillMount() {
        this.xScale = d3.scale.linear();
        this.xAxis = d3.svg.axis()
            .scale(this.xScale)
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
        let { transform, label, width } = this.props,
            labelElement = <text className='xAxis label' textAnchor='middle' x={width/2} y='30'>{label}</text>;
        return (
            <g ref='xAxis' className="x axis"
                transform={`translate(${transform[0]}, ${transform[1]})`}>
                {labelElement}
            </g>
        );
    }

    renderAxis() {
        let { min, max, width, padding } = this.props;
        this.xScale
            .domain([min, max])
            .range([padding[3], width - padding[1] - padding[3]]);

        d3.select(this.refs.xAxis).call(this.xAxis);
    }
}
