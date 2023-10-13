import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import Recommendation from "../components/Recommendation";

@inject("store")
@observer
class RecommendationTab extends React.Component {
    render() {
        let {store} = this.props;

        return (
            <Recommendation
                models={store.models}
                bmrs={store.bmrs}
                selectedModelId={store.selectedModelId}
                selectedModelNotes={store.selectedModelNotes}
            />
        );
    }
}
RecommendationTab.propTypes = {
    store: PropTypes.object,
};
export default RecommendationTab;
