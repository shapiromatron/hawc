import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import Plot from "react-plotly.js";

class PlotlyFigure extends Component {
    render() {
        const {data, layout} = this.props;
        return (
            <Plot
                data={data}
                layout={layout}
                useResizeHandler={true}
                style={{width: "100%", height: "100%"}}
            />
        );
    }
}
PlotlyFigure.propTypes = {
    data: PropTypes.array,
    layout: PropTypes.object,
};

const renderPlotlyFigure = function(el, config) {
    el.innerHTML = "";
    try {
        ReactDOM.render(<PlotlyFigure {...config} />, el);
    } catch (error) {
        el.innerHTML = '<span class="text-danger">An error occurred</span>';
    }
};

export {renderPlotlyFigure};
export default PlotlyFigure;
