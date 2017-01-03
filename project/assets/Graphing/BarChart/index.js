import React, { Component, PropTypes } from 'react';


class BarChart extends Component {

    render() {
        const { xScale, yScale, chartData, data } = this.props;
        return (
            <g>
                {data.map((bar, i) => {
                    let y = yScale(bar.key),
                        x = xScale(bar.values.count),
                        labelLength = bar.values.count.toString().length * 10,
                        height = yScale.rangeBand(),
                        width = x - chartData.padding.left;
                    return (
                    <g key={i}>
                        <rect
                            className='bar'
                            x={chartData.padding.left}
                            y={y}
                            width={width}
                            height={height}
                            fill={chartData.colors[bar.key]}
                        />
                        <text
                            y={y + height - 2}
                            x={(x - chartData.padding.left) > (labelLength) ? x - (labelLength) : x + 5}
                            fontSize={height - 3}>
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
