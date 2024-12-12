import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import Alert from "shared/components/Alert";
import FloatInput from "shared/components/FloatInput";
import SelectInput from "shared/components/SelectInput";
import WaitLoad from "shared/components/WaitLoad";

import DatasetTable from "./DatasetTable";
import DoseResponsePlot from "./DoseResponsePlot";

@inject("store")
@observer
class SettingsTab extends React.Component {
    render() {
        const {store} = this.props,
            readOnly = !store.config.edit,
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
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-8">
                        <DatasetTable />
                        {readOnly ? (
                            <table className="table table-sm table-striped">
                                <thead>
                                    <tr>
                                        <th>Setting</th>
                                        <th>Value</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Dose units</td>
                                        <td>{store.doseUnitsText}</td>
                                    </tr>
                                    {settings.num_doses_dropped > 0 ? (
                                        <tr>
                                            <td>Doses dropped</td>
                                            <td>{settings.num_doses_dropped}</td>
                                        </tr>
                                    ) : null}
                                    <tr>
                                        <td>BMR</td>
                                        <td>{store.bmrText}</td>
                                    </tr>
                                    {isContinuous ? (
                                        <tr>
                                            <td>Variance model</td>
                                            <td>{store.variableModelText}</td>
                                        </tr>
                                    ) : null}
                                </tbody>
                            </table>
                        ) : (
                            <div>
                                <div className="row">
                                    <div className="col-md-4">
                                        <SelectInput
                                            choices={doseUnitChoices}
                                            handleSelect={value =>
                                                changeSetting("dose_units_id", parseInt(value))
                                            }
                                            value={settings.dose_units_id.toString()}
                                            label="Dose Units"
                                            helpText="..."
                                        />
                                    </div>
                                    <div className="col-md-4">
                                        <SelectInput
                                            choices={doseDropChoices}
                                            handleSelect={value =>
                                                changeSetting("num_doses_dropped", parseInt(value))
                                            }
                                            value={settings.num_doses_dropped.toString()}
                                            label="Doses to Drop"
                                            helpText="..."
                                        />
                                    </div>
                                    <div className="col-md-4"></div>
                                    <div className="col-md-4">
                                        <SelectInput
                                            choices={bmrTypeChoices}
                                            handleSelect={value =>
                                                changeSetting("bmr_type", parseInt(value))
                                            }
                                            value={settings.bmr_type.toString()}
                                            label="BMR Type"
                                            helpText="..."
                                        />
                                    </div>
                                    <div className="col-md-4">
                                        <FloatInput
                                            label="BMR"
                                            name="BMR"
                                            value={settings.bmr_value}
                                            onChange={e =>
                                                changeSetting(
                                                    "bmr_value",
                                                    parseFloat(e.target.value)
                                                )
                                            }
                                            helpText="..."
                                        />
                                    </div>
                                    <div className="col-md-4">
                                        {isContinuous ? (
                                            <SelectInput
                                                choices={varianceModelChoices}
                                                handleSelect={value =>
                                                    changeSetting("variance_model", parseInt(value))
                                                }
                                                value={settings.variance_model.toString()}
                                                label="Variance model"
                                                helpText="..."
                                            />
                                        ) : null}
                                    </div>
                                </div>
                                <button
                                    className="btn btn-primary btn-block my-3 py-3"
                                    disabled={store.isExecuting}
                                    onClick={store.saveAndExecute}>
                                    <i className="fa fa-fw fa-play-circle"></i>&nbsp;Execute
                                    Analysis
                                </button>
                                {store.isExecuting ? (
                                    <Alert
                                        className="alert-info"
                                        icon="fa-spinner fa-spin fa-2x"
                                        message="Executing, please wait..."
                                    />
                                ) : null}
                                {executionError ? (
                                    <Alert
                                        message="An error occurred. If the problem persists, please
                                        contact the site administrators."
                                    />
                                ) : null}
                            </div>
                        )}
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
