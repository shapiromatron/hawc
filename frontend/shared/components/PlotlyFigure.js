import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";
import Plot from "react-plotly.js";

class PlotlyFigure extends Component {
    constructor(props) {
        super(props);
        this.ref = React.createRef();
    }
    componentDidMount() {
        this.observer = new window.ResizeObserver(
            _.debounce(item => window.dispatchEvent(new Event("resize"))),
            1000
        );
        this.observer.observe(this.ref.current);
    }
    componentWillUnmount() {
        this.observer.unobserve();
    }
    render() {
        const {data, layout} = this.props;
        const attrs = (this.props.resizable)? style={{resize: "both", overflow: "hidden"}, ref:{this.ref}}: {};
        return (
            <div ...attrs>
                <Plot
                    data={data}
                    layout={layout}
                    useResizeHandler={true}
                    style={{width: "100%", height: "100%"}}
                />
            </div>
        );
    }
}
PlotlyFigure.propTypes = {
    resizable: PropTypes.bool,
    data: PropTypes.array,
    layout: PropTypes.object,
};
PlotlyFigure.defaultProps = {
    resizable: true,
};

const renderPlotlyFigure = function(el, config) {
    el.innerHTML = "";
    try {
        ReactDOM.render(<PlotlyFigure {...config} />, el);
    } catch (error) {
        el.innerHTML = '<span class="text-danger">An error occurred</span>';
        console.error(error);
    }
};

export {renderPlotlyFigure};
export default PlotlyFigure;
