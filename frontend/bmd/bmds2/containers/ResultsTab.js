import React from "react";
import {inject, observer} from "mobx-react";
import _ from "lodash";
import PropTypes from "prop-types";

import RecommendationNotes from "../components/RecommendationNotes";
import OutputTable from "../components/OutputTable";
import OutputFigure from "../components/OutputFigure";

@inject("store")
@observer
class ResultsTab extends React.Component {
    render() {
        let {store} = this.props,
            selectedModel = _.find(store.models, {id: store.selectedModelId}) || null;

        return (
            <>
                <h3>BMDS output summary</h3>
                <div className="row-fluid">
                    <OutputTable
                        models={store.models}
                        bmrs={store.bmrs}
                        handleModal={models => store.showOutputModal(models)}
                        handleModelHover={model => store.setHoverModel(model)}
                        handleModelNoHover={() => store.setHoverModel(null)}
                        selectedModelId={store.selectedModelId}
                    />
                    <OutputFigure
                        endpoint={store.endpoint}
                        hoverModel={store.hoverModel}
                        selectedModel={selectedModel}
                    />
                </div>
                <RecommendationNotes notes={store.selectedModelNotes} />
            </>
        );
    }
}
ResultsTab.propTypes = {
    store: PropTypes.object,
};
export default ResultsTab;
