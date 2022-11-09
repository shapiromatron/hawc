import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import BMROptionModal from "../components/BMROptionModal";
import ModelOptionModal from "../components/ModelOptionModal";
import OutputModal from "../components/OutputModal";

@inject("store")
@observer
class Modals extends React.Component {
    render() {
        const {store} = this.props,
            {config} = store;

        return (
            <div>
                <ModelOptionModal
                    model={store.selectedModelOption}
                    editMode={config.editMode}
                    handleSave={values => store.updateModel(values)}
                    handleDelete={store.deleteModel}
                />
                <BMROptionModal
                    bmr={store.selectedBmr}
                    allOptions={store.allBmrOptions}
                    editMode={config.editMode}
                    handleSave={values => store.updateBmr(values)}
                    handleDelete={store.deleteBmr}
                />
                <OutputModal models={store.selectedOutputs} />
            </div>
        );
    }
}

Modals.propTypes = {
    store: PropTypes.object,
};

export default Modals;
