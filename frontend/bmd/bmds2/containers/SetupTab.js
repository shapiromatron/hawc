import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import {toJS} from "mobx";
import BMROptionTable from "../components/BMROptionTable";
import DoseResponse from "../components/DoseResponse";
import ModelOptionTable from "../components/ModelOptionTable";

@inject("store")
@observer
class SetupTab extends React.Component {
    render() {
        const {store} = this.props;

        return (
            <>
                <DoseResponse endpoint={store.endpoint} />
                <h3>Selected models and options</h3>
                <div className="row">
                    <ModelOptionTable
                        dataType={store.dataType}
                        handleModalDisplay={modelIndex => store.showOptionModal(modelIndex)}
                        models={toJS(store.modelSettings)}
                        allOptions={store.allModelOptions}
                    />
                    <BMROptionTable
                        handleModalDisplay={bmrIndex => store.showBmrModal(bmrIndex)}
                        bmrs={toJS(store.bmrs)}
                    />
                </div>
            </>
        );
    }
}
SetupTab.propTypes = {
    store: PropTypes.object,
};
export default SetupTab;
