import React, {Component} from "react";
import PropTypes from "prop-types";
import d3 from "d3";

class xAxis extends Component {
    componentDidMount() {
        let {xScale, ticks} = this.props;
        this.xAxis = d3.svg
            .axis()
            .scale(xScale)
            .orient("bottom")
            .ticks(ticks);
        this.renderAxis();
    }

    componentDidUpdate() {
        this.renderAxis();
    }

    getLabelElement(axisLabel) {
        let {padding} = this.props;
        return (
            <text
                className="xAxis label"
                textAnchor="beginning"
                x={padding.left + 10}
                y={axisLabel.offset}>
                {axisLabel.label}
            </text>
        );
    }

    render() {
        let {transform, label, padding, renderScale} = this.props,
            axisLabel = renderScale
                ? {offset: padding.bottom - 15, label}
                : {offset: 20, label: label.substr(0, label.indexOf(" "))},
            labelElement = this.getLabelElement(axisLabel);
        return (
            <g
                ref="xAxis"
                className="x axis"
                transform={`translate(${transform[0]}, ${transform[1]})`}>
                {labelElement}
            </g>
        );
    }

    renderAxis() {
        this.props.xScale();
        this.props.renderScale ? d3.select(this.refs.xAxis).call(this.xAxis) : null;
    }
}

xAxis.propTypes = {
    width: PropTypes.number.isRequired,
    padding: PropTypes.shape({
        top: PropTypes.number.isRequired,
        right: PropTypes.number.isRequired,
        bottom: PropTypes.number.isRequired,
        left: PropTypes.number.isRequired,
    }).isRequired,
    transform: PropTypes.arrayOf(PropTypes.number.isRequired).isRequired,
    label: PropTypes.string.isRequired,
    renderScale: PropTypes.bool,
    xScale: PropTypes.func.isRequired,
    ticks: PropTypes.oneOfType([PropTypes.array, PropTypes.number]).isRequired,
};

export default xAxis;
