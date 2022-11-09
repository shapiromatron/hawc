import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";

import BMROptionTable from "../components/BMROptionTable";
import DoseResponse from "../components/DoseResponse";
import DoseUnitsSelector from "../components/DoseUnitsSelector";
import ExecuteWell from "../components/ExecuteWell";
import ModelOptionTable from "../components/ModelOptionTable";

@inject("store")
@observer
class SetupTab extends React.Component {
    render() {
        const {store} = this.props,
            {config} = store;

        return (
            <>
                <DoseResponse endpoint={store.endpoint} />
                <h3>Selected models and options</h3>
                <DoseUnitsSelector
                    version={config.bmds_version}
                    editMode={config.editMode}
                    endpoint={store.endpoint}
                    doseUnits={store.doseUnits}
                    handleUnitsChange={doseUnits => store.changeUnits(doseUnits)}
                />
                <div className="row">
                    <ModelOptionTable
                        editMode={config.editMode}
                        dataType={store.dataType}
                        handleVarianceToggle={() => store.toggleVariance()}
                        handleAddAll={() => store.addAllModels()}
                        handleRemoveAll={() => store.removeAllModels()}
                        handleCreateModel={modelName => store.createModel(modelName)}
                        handleModalDisplay={modelIndex => store.showOptionModal(modelIndex)}
                        models={store.modelSettings.toJS()}
                        allOptions={store.allModelOptions}
                    />

                    <BMROptionTable
                        editMode={config.editMode}
                        handleCreateBmr={() => store.createBmr()}
                        handleModalDisplay={bmrIndex => store.showBmrModal(bmrIndex)}
                        bmrs={store.bmrs.toJS()}
                    />
                </div>
                <ExecuteWell
                    editMode={config.editMode}
                    validationErrors={store.validationErrors}
                    isExecuting={store.isExecuting}
                    handleExecute={store.tryExecute}
                />
            </>
        );
    }
}
SetupTab.propTypes = {
    store: PropTypes.object,
};
export default SetupTab;
