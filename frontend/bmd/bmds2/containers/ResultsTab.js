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
            <div className="row">
                <div className="col-md-12">
                    <h3>BMDS output summary</h3>
                </div>
                <div className="col-md-8">
                    <OutputTable
                        models={store.models}
                        bmrs={store.bmrs}
                        handleModal={models => store.showOutputModal(models)}
                        handleModelHover={model => store.setHoverModel(model)}
                        handleModelNoHover={() => store.setHoverModel(null)}
                        selectedModelId={store.selectedModelId}
                    />
                    <RecommendationNotes notes={store.selectedModelNotes} />
                </div>
                <div className="col-md-4">
                    <OutputFigure
                        endpoint={store.endpoint}
                        hoverModel={store.hoverModel}
                        selectedModel={selectedModel}
                    />
                </div>
            </div>
        );
    }
}
ResultsTab.propTypes = {
    store: PropTypes.object,
};
export default ResultsTab;
