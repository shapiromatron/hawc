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
        const {store} = this.props;

        return (
            <div>
                <ModelOptionModal model={store.selectedModelOption} />
                <BMROptionModal bmr={store.selectedBmr} allOptions={store.allBmrOptions} />
                <OutputModal models={store.selectedOutputs} />
            </div>
        );
    }
}

Modals.propTypes = {
    store: PropTypes.object,
};

export default Modals;
