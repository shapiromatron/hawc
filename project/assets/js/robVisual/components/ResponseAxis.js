import React, { Component } from 'react';

export default class ResponseAxis extends Component {

    componentWillMount() {
        this.xScale = d3.scale.linear();
        this.xAxis = d3.svg.axis()
            .scale(this.xScale)
            .orient('bottom');
    }

    componentDidMount() {
        this.renderAxis();
    }

    compnentDidUpdate() {
        this.renderAxis();
    }

    render() {
        return <g ref='responseAxis' className="y axis" />;
    }

    renderAxis() {
        this.xScale
            .domain([0, this.props.max])
            .range([0, this.props.width]);

        d3.select(this.refs.responseAxis).call(this.xAxis);
    }
}
