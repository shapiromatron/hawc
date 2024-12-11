import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import PlotlyFigure from "shared/components/PlotlyFigure";

@inject("store")
@observer
class DoseResponsePlot extends React.Component {
    render() {
        const config = this.props.store.drPlotConfig;
        return <PlotlyFigure data={config.data} layout={config.layout} />;
    }
}
DoseResponsePlot.propTypes = {
    store: PropTypes.object,
};

export default DoseResponsePlot;
