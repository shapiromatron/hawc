import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import FloatInput from "shared/components/FloatInput";
import Loading from "shared/components/Loading";
import SelectInput from "shared/components/SelectInput";

import DoseResponse from "/bmd/bmds2/components/DoseResponse";

@inject("store")
@observer
class Root extends React.Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchSession();
    }
    render() {
        const {store} = this.props,
            readOnly = !store.config.edit;

        if (!store.hasSessionLoaded) {
            return <Loading />;
        }

        const {
            doseUnitChoices,
            doseDropChoices,
            bmrTypeChoices,
            varianceModelChoices,
            endpoint,
            settings,
            changeSetting,
            isContinuous,
        } = store;

        return (
            <Tabs>
                <TabList>
                    <Tab>Settings</Tab>
                    <Tab className="react-tabs__tab bmd-results-tab">Results</Tab>
                </TabList>
                <TabPanel>
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-md-12 pb-5">
                                <DoseResponse endpoint={endpoint} />
                            </div>
                        </div>
                        {readOnly ? (
                            <div className="row">
                                <h3 className="col-md-12">BMD modeling settings</h3>
                                <div className="col-md-8">
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
                                </div>
                            </div>
                        ) : (
                            <div className="row">
                                <h3 className="col-md-12">BMD modeling settings</h3>
                                <div className="col-md-9">
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
                                                    changeSetting(
                                                        "num_doses_dropped",
                                                        parseInt(value)
                                                    )
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
                                                onChange={value =>
                                                    changeSetting("bmr_value", value)
                                                }
                                                helpText="..."
                                            />
                                        </div>

                                        <div className="col-md-4">
                                            {isContinuous ? (
                                                <SelectInput
                                                    choices={varianceModelChoices}
                                                    handleSelect={value =>
                                                        changeSetting(
                                                            "variance_model",
                                                            parseInt(value)
                                                        )
                                                    }
                                                    value={settings.variance_model.toString()}
                                                    label="Variance model"
                                                    helpText="..."
                                                />
                                            ) : null}
                                        </div>
                                    </div>
                                </div>

                                <div className="col-md-3 bg-light">
                                    <button
                                        className="btn btn-primary btn-block my-3 py-3"
                                        disabled={store.isExecuting}
                                        onClick={store.saveAndExecute}>
                                        <i className="fa fa-fw fa-play-circle"></i>&nbsp;Execute
                                        Analysis
                                    </button>
                                    {store.isExecuting ? (
                                        <div className="alert alert-info mt-2">
                                            Executing, please wait...
                                            <i className="fa fa-spinner fa-spin fa-fw fa-2x"></i>
                                        </div>
                                    ) : null}
                                </div>
                            </div>
                        )}
                    </div>
                </TabPanel>
                <TabPanel>
                    <div className="container-fluid">
                        <div className="row">
                            <div className="col-md-8">
                                <h3>Summary Table</h3>
                            </div>
                            <div className="col-md-4">
                                <h3>Summary Figure</h3>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-md-12">
                                <h3>Model Selection</h3>
                            </div>
                        </div>
                    </div>
                </TabPanel>
            </Tabs>
        );
    }
}
Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
