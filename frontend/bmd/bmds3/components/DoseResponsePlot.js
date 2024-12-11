import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import PlotlyFigure from "shared/components/PlotlyFigure";

@inject("store")
@observer
class DoseResponsePlot extends React.Component {
    render() {
        const {store} = this.props;
        return (
            <PlotlyFigure
                data={_.compact(
                    _.flatten([
                        this.props.showDataset ? store.drPlotDataset : null,
                        this.props.showSelected ? store.drPlotSelectedData : null,
                        this.props.showHover ? store.drPlotHover : null,
                        this.props.showModal ? store.drPlotModal : null,
                    ])
                )}
                layout={store.drPlotLayout}
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
    showDataset: PropTypes.bool,
    showSelected: PropTypes.bool,
    showHover: PropTypes.bool,
    showModal: PropTypes.bool,
};
DoseResponsePlot.defaultProps = {
    showDataset: false,
    showSelected: false,
    showHover: false,
    showModal: false,
};

export default DoseResponsePlot;
