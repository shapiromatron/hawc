import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import Recommendation from "../components/Recommendation";

@inject("store")
@observer
class RecommendationTab extends React.Component {
    render() {
        let {store} = this.props,
            {config} = store;

        return (
            <Recommendation
                editMode={config.editMode}
                models={store.models}
                bmrs={store.bmrs}
                selectedModelId={store.selectedModelId}
                selectedModelNotes={store.selectedModelNotes}
                handleSaveSelected={(model_id, notes) => store.saveSelectedModel(model_id, notes)}
            />
        );
    }
}
RecommendationTab.propTypes = {
    store: PropTypes.object,
};
export default RecommendationTab;
