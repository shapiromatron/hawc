import React from "react";
import {observer} from "mobx-react";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";
import SelectInput from "shared/components/SelectInput";
import {selectedModelChoices} from "./constants";
import Plot from "react-plotly.js";

@observer
class Root extends React.Component {
    componentDidMount() {
        this.props.store.fetchNewChart();
    }

    renderSelectInput(store) {
        return (
            <SelectInput
                id="selectedModel"
                choices={selectedModelChoices}
                handleSelect={() => store.changeSelectedModel(parseInt(event.target.value))}
                value={store.selectedModel}
                label="Select model to view results"
            />
        );
    }

    renderVisualization(store) {
        if (store.isFetchingData) {
            return <Loading />;
        }
        if (store.plotData === null) {
            return <p>-</p>;
        }
        return <Plot data={store.plotData.data} layout={store.plotData.layout} />;
    }

    render() {
        let {store} = this.props;
        return (
            <div>
                {this.renderSelectInput(store)}
                {this.renderVisualization(store)}
            </div>
        );
    }
}

Root.propTypes = {
    store: PropTypes.shape({
        selectedModel: PropTypes.number.isRequired,
        changeSelectedModel: PropTypes.func.isRequired,
        plotData: PropTypes.object,
    }).isRequired,
};

export default Root;
