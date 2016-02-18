import React, { Component } from 'react';

export default class LineChart extends Component {

    componentWillMount() {
        this.line = d3.svg.line()
            .x((d) => { return d.x; })
            .y((d) => { return d.y; });
    }

    render() {
        return (
            <g>
                {/*<path d={this.line(this.props)} />*/}
            </g>
        );
    }
}
