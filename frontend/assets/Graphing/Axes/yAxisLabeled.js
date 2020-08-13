import React, {Component} from "react";
import PropTypes from "prop-types";
import * as d3 from "d3";

class yAxisLabeled extends Component {
    componentDidMount() {
        let {yScale, ticks} = this.props;
        this.yAxisContainer = React.createRef();
        this.yAxis = d3.svg
            .axis()
            .scale(yScale)
            .orient("left")
            .tickFormat(ticks);
        this.renderAxis();
    }

    componentDidUpdate() {
        this.renderAxis();
    }

    getLabelElement(axisLabel) {
        let {height, padding} = this.props;
        return (
            <text
                className="yAxis label"
                textAnchor="beginning"
                y={`-${axisLabel.offset}`}
                x={padding.bottom - height}
                transform={"rotate(-90)"}>
                {axisLabel.label}
            </text>
        );
    }

    render() {
        let {transform, label, padding, renderScale} = this.props,
            axisLabel = renderScale
                ? {offset: padding.left - 20, label}
                : {offset: 20, label: label.substr(0, label.indexOf(" "))},
            labelElement = this.getLabelElement(axisLabel);
        return (
            <g
                ref={this.yAxisContainer}
                className="y axis"
                transform={`translate(${transform[0]}, ${transform[1]})`}>
                {labelElement}
            </g>
        );
    }

    renderAxis() {
        this.props.yScale();
        this.props.renderScale ? d3.select(this.yAxisContainer.current).call(this.yAxis) : null;
    }
}

yAxisLabeled.propTypes = {
    min: PropTypes.number,
    max: PropTypes.number,
    height: PropTypes.number.isRequired,
    padding: PropTypes.shape({
        top: PropTypes.number.isRequired,
        right: PropTypes.number.isRequired,
        bottom: PropTypes.number.isRequired,
        left: PropTypes.number.isRequired,
    }).isRequired,
    transform: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    label: PropTypes.string.isRequired,
    renderScale: PropTypes.bool,
    yScale: PropTypes.func.isRequired,
    ticks: PropTypes.func,
};

export default yAxisLabeled;
