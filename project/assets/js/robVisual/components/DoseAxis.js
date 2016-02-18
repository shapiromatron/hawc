import React, { Component } from 'react';

export default class DoseAxis extends Component {
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
        return <g ref='doseAxis' className='y axis'/>;
    }

    renderAxis() {
        let { minDose, maxDose, height } = this.props;
        this.yScale
            .domain([minDose, maxDose])
            .range([0, height]);
        d3.select(this.refs.doseAxis).call(this.yAxis);
    }
}
