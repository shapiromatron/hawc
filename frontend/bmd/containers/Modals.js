import React from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import ModelOptionModal from "bmd/components/ModelOptionModal";
import BMROptionModal from "bmd/components/BMROptionModal";
import OutputModal from "bmd/components/OutputModal";

@inject("store")
@observer
class Modals extends React.Component {
    render() {
        const {store} = this.props,
            {allBmrOptions, selectedModelOption, selectedBmr, selectedOutputs} = store,
            isReady = allBmrOptions !== null,
            {editMode} = store.config;

        if (!isReady) {
            return null;
        }

        return (
            <div>
                <ModelOptionModal
                    model={selectedModelOption}
                    editMode={editMode}
                    handleSave={values => store.updateModel(values)}
                    handleDelete={store.deleteModel}
                />
                <BMROptionModal
                    bmr={selectedBmr}
                    allOptions={allBmrOptions}
                    editMode={editMode}
                    handleSave={values => store.updateBmr(values)}
                    handleDelete={store.deleteBmr}
                />
                <OutputModal models={selectedOutputs} />
            </div>
        );
    }
}

Modals.propTypes = {
    store: PropTypes.object,
};

export default Modals;
