import React, {Component} from "react";
import PropTypes from "prop-types";

import "./BarChart.css";

class BarChart extends Component {
    render() {
        const {xScale, yScale, chartData, data} = this.props;
        return (
            <g>
                {data.map((bar, i) => {
                    let y = yScale(bar.key),
                        x = xScale(bar.values.count),
                        height = yScale.bandwidth(),
                        width = x - chartData.padding.left,
                        labelText = width > 25 ? "bar-chart-label-left" : "bar-chart-label-right",
                        labelOffset = width > 25 ? -5 : 2;

                    return (
                        <g key={i}>
                            <rect
                                className="bar"
                                x={chartData.padding.left}
                                y={y}
                                width={width}
                                height={height}
                                fill={chartData.colors[bar.key]}
                            />
                            <text
                                className={labelText}
                                y={y + height / 2}
                                x={chartData.padding.left + width + labelOffset}>
                                {bar.values.count}
                            </text>
                        </g>
                    );
                })}
            </g>
        );
    }
}

BarChart.propTypes = {
    chartData: PropTypes.shape({
        colors: PropTypes.object.isRequired,
        padding: PropTypes.shape({
            top: PropTypes.number.isRequired,
            right: PropTypes.number.isRequired,
            bottom: PropTypes.number.isRequired,
            left: PropTypes.number.isRequired,
        }).isRequired,
    }).isRequired,
    data: PropTypes.arrayOf(
        PropTypes.shape({
            key: PropTypes.string.isRequired,
            values: PropTypes.shape({
                count: PropTypes.number.isRequired,
            }).isRequired,
        }).isRequired
    ).isRequired,
    xScale: PropTypes.func.isRequired,
    yScale: PropTypes.func.isRequired,
};

export default BarChart;
