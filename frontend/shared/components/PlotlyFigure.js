import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import Plot from "react-plotly.js";

class ResizableDiv extends Component {
    /*
    User-resizable div; when div is resized, triggers window resize event,
    which Plotly uses to resize the figure.  Currently set to debounce sizing;
    Plotly figure will re-render at most every 500ms.
    */
    constructor(props) {
        super(props);
        this.ref = React.createRef();
    }
    componentDidMount() {
        this.observer = new window.ResizeObserver(
            _.debounce(el => window.dispatchEvent(new Event("resize")), 500)
        );
        this.observer.observe(this.ref.current);
    }
    componentWillUnmount() {
        this.observer.unobserve();
    }
    render() {
        const {children} = this.props;
        return (
            <div ref={this.ref} style={{resize: "both", overflow: "hidden"}}>
                {children}
            </div>
        );
    }
}
ResizableDiv.propTypes = {
    children: PropTypes.element.isRequired,
};

class PlotlyFigure extends Component {
    render() {
        const {data, layout, config, resizable} = this.props,
            plot = (
                <Plot
                    data={data}
                    layout={layout}
                    config={config}
                    useResizeHandler={true}
                    style={{width: "100%", height: "100%"}}
                />
            );
        return resizable ? <ResizableDiv>{plot}</ResizableDiv> : plot;
    }
}
PlotlyFigure.propTypes = {
    data: PropTypes.array,
    layout: PropTypes.object,
    config: PropTypes.object,
    resizable: PropTypes.bool,
};
PlotlyFigure.defaultProps = {
    config: {
        modeBarButtonsToRemove: [
            "pan2d",
            "select2d",
            "lasso2d",
            "zoomIn2d",
            "zoomOut2d",
            "autoScale2d",
            "hoverClosestCartesian",
            "hoverCompareCartesian",
            "toggleSpikelines",
        ],
    },
    resizable: false,
};

const renderPlotlyFigure = function(el, config, resizable = false) {
    el.innerHTML = "";
    try {
        ReactDOM.render(<PlotlyFigure {...config} resizable={resizable} />, el);
    } catch (error) {
        el.innerHTML = '<span class="text-danger">An error occurred</span>';
        console.error(error);
    }
};

export {renderPlotlyFigure};
export default PlotlyFigure;
