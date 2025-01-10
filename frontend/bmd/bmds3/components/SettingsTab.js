import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import Alert from "shared/components/Alert";
import FloatInput from "shared/components/FloatInput";
import SelectInput from "shared/components/SelectInput";
import WaitLoad from "shared/components/WaitLoad";

import DatasetTable from "./DatasetTable";
import DoseResponsePlot from "./DoseResponsePlot";
import Table from "./Table";

@inject("store")
@observer
class SettingsTable extends React.Component {
    render() {
        const {store, showRunMetadata} = this.props,
            {settings, isContinuous} = store;
        return (
            <Table
                colWidths={[40, 60]}
                colNames={["Setting", "Value"]}
                data={_.compact([
                    ["Dose Units", store.doseUnitsText],
                    ["BMR", store.bmrText],
                    isContinuous ? ["Variance Model", store.varianceModelText] : null,
                    settings.num_doses_dropped > 0
                        ? ["Doses Dropped", settings.num_doses_dropped]
                        : null,
                    showRunMetadata ? ["pybmds Version", store.pybmdsVersion] : null,
                    showRunMetadata ? ["Execution Date", store.executionDate] : null,
                ])}
            />
        );
    }
}
SettingsTable.propTypes = {
    store: PropTypes.object,
    showRunMetadata: PropTypes.bool,
};
SettingsTable.defaultProps = {
    showRunMetadata: false,
};

@inject("store")
@observer
class SettingsForm extends React.Component {
    render() {
        const {store} = this.props,
            {
                doseUnitChoices,
                doseDropChoices,
                bmrTypeChoices,
                varianceModelChoices,
                settings,
                changeSetting,
                isContinuous,
                executionError,
            } = store;

        return (
            <div className="row">
                <div className="col-md-4">
                    <SelectInput
                        choices={doseUnitChoices}
                        handleSelect={value => changeSetting("dose_units_id", parseInt(value))}
                        value={settings.dose_units_id.toString()}
                        label="Dose Units"
                        helpText="Select which dose units to use for modeling. You can create different sessions with different dose units."
                    />
                </div>
                <div className="col-md-4">
                    <SelectInput
                        choices={doseDropChoices}
                        handleSelect={value => changeSetting("num_doses_dropped", parseInt(value))}
                        value={settings.num_doses_dropped.toString()}
                        label="Doses to Drop"
                        helpText="Remove dose groups from modeling; the highest groups are removed."
                    />
                </div>
                <div className="col-md-4"></div>
                <div className="col-md-4">
                    <SelectInput
                        choices={bmrTypeChoices}
                        handleSelect={value => changeSetting("bmr_type", parseInt(value))}
                        value={settings.bmr_type.toString()}
                        label="BMR Type"
                        helpText="Benchmark response type."
                    />
                </div>
                <div className="col-md-4">
                    <FloatInput
                        label="BMR"
                        name="BMR"
                        value={settings.bmr_value}
                        onChange={e => changeSetting("bmr_value", parseFloat(e.target.value))}
                        helpText="Benchmark response value."
                    />
                </div>
                <div className="col-md-4">
                    {isContinuous ? (
                        <SelectInput
                            choices={varianceModelChoices}
                            handleSelect={value => changeSetting("variance_model", parseInt(value))}
                            value={settings.variance_model.toString()}
                            label="Variance model"
                            helpText="Which variance model to use."
                        />
                    ) : null}
                </div>
                <div className="col-12 px-5">
                    <button
                        className="btn btn-primary btn-block my-3 py-3"
                        disabled={store.isExecuting}
                        onClick={store.saveAndExecute}>
                        <i className="fa fa-fw fa-play-circle"></i>&nbsp;Execute Analysis
                    </button>
                    {store.isExecuting ? (
                        <Alert
                            className="alert-info d-flex align-items-center"
                            icon="fa-spinner fa-spin fa-2x"
                            message="Executing, please wait ..."
                            testId="executing-spinner"
                        />
                    ) : null}
                    {executionError ? <Alert /> : null}
                </div>
            </div>
        );
    }
}
SettingsForm.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class SettingsTab extends React.Component {
    render() {
        const {store} = this.props,
            readOnly = !store.config.edit;
        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-8">
                        <DatasetTable />
                        {readOnly ? <SettingsTable /> : <SettingsForm />}
                    </div>
                    <div className="col-lg-4">
                        <WaitLoad>
                            <div style={{height: "400px"}}>
                                <DoseResponsePlot showDataset={true} />
                            </div>
                        </WaitLoad>
                    </div>
                </div>
            </div>
        );
    }
}
SettingsTab.propTypes = {
    store: PropTypes.object,
};

export default SettingsTab;
export {SettingsTable};
