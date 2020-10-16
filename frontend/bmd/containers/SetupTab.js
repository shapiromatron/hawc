import React from "react";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";

import DoseResponse from "bmd/components/DoseResponse";
import DoseUnitsSelector from "bmd/components/DoseUnitsSelector";
import ModelOptionTable from "bmd/components/ModelOptionTable";
import BMROptionTable from "bmd/components/BMROptionTable";
import ExecuteWell from "bmd/components/ExecuteWell";

@inject("store")
@observer
class SetupTab extends React.Component {
    render() {
        let {store} = this.props,
            {editMode, bmds_version} = this.props.store.config;

        return (
            <>
                <DoseResponse endpoint={store.endpoint} />
                <h3>Selected models and options</h3>
                <DoseUnitsSelector
                    version={bmds_version}
                    editMode={editMode}
                    endpoint={store.endpoint}
                    doseUnits={store.doseUnits}
                    handleUnitsChange={doseUnits => store.changeUnits(doseUnits)}
                />
                <div className="row-fluid">
                    <ModelOptionTable
                        editMode={editMode}
                        dataType={store.dataType}
                        handleVarianceToggle={() => store.toggleVariance()}
                        handleAddAll={() => store.addAllModels()}
                        handleRemoveAll={() => store.removeAllModels()}
                        handleCreateModel={modelName => store.createModel(modelName)}
                        handleModalDisplay={modelIndex => store.showOptionModal(modelIndex)}
                        models={store.modelSettings}
                        allOptions={store.allModelOptions}
                    />
                    <BMROptionTable
                        editMode={editMode}
                        handleCreateBmr={() => store.createBmr()}
                        handleModalDisplay={bmrIndex => store.showBmrModal(bmrIndex)}
                        bmrs={store.bmrs}
                    />
                </div>
                <ExecuteWell
                    editMode={editMode}
                    validationErrors={store.validationErrors}
                    isExecuting={store.isExecuting}
                    handleExecute={() => store.tryExecute()}
                />
            </>
        );
    }
}
SetupTab.propTypes = {
    store: PropTypes.object,
};
export default SetupTab;
