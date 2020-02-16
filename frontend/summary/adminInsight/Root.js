import React from "react";
import {observer} from "mobx-react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";
import SelectInput from "shared/components/SelectInput";
import {modelChoices, grouperChoices} from "./constants";
import Plot from "react-plotly.js";

@observer
class Root extends React.Component {
    componentDidMount() {
        this.props.store.growthStore.fetchNewChart();
    }

    renderInputs(store) {
        return (
            <div>
                <SelectInput
                    id="model"
                    choices={modelChoices}
                    handleSelect={() => store.changeQueryValue("model", event.target.value)}
                    value={store.query.model}
                    label="Select model to view results"
                />
                <SelectInput
                    id="selectedModel"
                    choices={grouperChoices}
                    handleSelect={() => store.changeQueryValue("grouper", event.target.value)}
                    value={store.query.grouper}
                    label="Select grouping frequency"
                />
            </div>
        );
    }

    renderVisualization(store) {
        if (store.isFetchingPlot || store.plotData === null) {
            return <Loading />;
        }
        return <Plot data={store.plotData.data} layout={store.plotData.layout} />;
    }

    render() {
        let store = this.props.store.growthStore;
        return (
            <div>
                {this.renderInputs(store)}
                {this.renderVisualization(store)}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.shape({
        growthStore: PropTypes.shape({
            query: PropTypes.shape({
                model: PropTypes.number.isRequired,
                grouper: PropTypes.number.isRequired,
            }),
            changeQueryValue: PropTypes.func.isRequired,
            fetchNewChart: PropTypes.func.isRequired,
            plotData: PropTypes.object,
        }).isRequired,
    }).isRequired,
};

export default Root;
