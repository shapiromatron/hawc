import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import PlotlyFigure from "shared/components/PlotlyFigure";

@inject("store")
@observer
class DoseResponsePlot extends React.Component {
    render() {
        const config = this.props.store.drPlotConfig;
        return (
            <PlotlyFigure
                data={config.data}
                layout={config.layout}
                config={{
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
                }}
            />
        );
    }
}
DoseResponsePlot.propTypes = {
    store: PropTypes.object,
};

export default DoseResponsePlot;
