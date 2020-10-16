import React from "react";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";

import Recommendation from "bmd/components/Recommendation";

@inject("store")
@observer
class RecommendationTab extends React.Component {
    render() {
        let {store} = this.props,
            {editMode} = store.config;

        return (
            <Recommendation
                editMode={editMode}
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
