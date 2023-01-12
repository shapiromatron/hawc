import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import FloatInput from "shared/components/FloatInput";
import Loading from "shared/components/Loading";
import SelectInput from "shared/components/SelectInput";
import TextAreaInput from "shared/components/TextAreaInput";
import h from "shared/utils/helpers";

import DoseResponse from "/bmd/bmds2/components/DoseResponse";
import OutputFigure from "/bmd/bmds2/components/OutputFigure";

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
                executionError,
                hasOutputs,
                selected,
            } = store,
            selected_model_index = store.selected.model_index;

        const defaultTabIndex = hasOutputs ? 1 : 0;

        return (
            <Tabs defaultIndex={defaultTabIndex}>
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
                                    {executionError ? (
                                        <div className="alert alert-danger">
                                            <i className="fa fa-exclamation-triangle fa-fw"></i>
                                            &nbsp; An error occurred. If the problem persists,
                                            please contact the site administrators.
                                        </div>
                                    ) : null}
                                </div>
                            </div>
                        )}
                    </div>
                </TabPanel>
                <TabPanel>
                    <div className="container-fluid">
                        {store.hasErrors ? (
                            <div className="row">
                                <div className="col-md-12">
                                    <h3>Execution Error</h3>
                                    <div className="alert alert-danger">
                                        <p>
                                            <i className="fa fa-exclamation-triangle fa-fw"></i> An
                                            error occurred:
                                        </p>
                                        {store.errors.traceback ? (
                                            <pre>{store.errors.traceback}</pre>
                                        ) : null}
                                    </div>
                                </div>
                            </div>
                        ) : null}
                        {store.hasOutputs ? (
                            <>
                                <div className="row">
                                    <div className="col-xl-8">
                                        <h3>Summary Table</h3>
                                        <table className="table table-sm table-striped table-hover text-right col-l-1">
                                            <colgroup>
                                                <col width="12%" />
                                                <col width="8%" />
                                                <col width="8%" />
                                                <col width="8%" />
                                                <col width="8%" />
                                                <col width="8%" />
                                                <col width="10%" />
                                                <col width="10%" />
                                                <col width="28%" />
                                            </colgroup>
                                            <thead>
                                                <tr>
                                                    <th>Model Name</th>
                                                    <th>BMDL ({store.doseUnitsText})</th>
                                                    <th>BMD ({store.doseUnitsText})</th>
                                                    <th>BMDU ({store.doseUnitsText})</th>
                                                    <th>
                                                        <i>P</i>-Value
                                                    </th>
                                                    <th>AIC</th>
                                                    <th>Scaled Residual for Dose Group near BMD</th>
                                                    <th>Scaled Residual for Control Dose Group</th>
                                                    <th>
                                                        Recommendation
                                                        <br />
                                                        and Notes
                                                    </th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {store.outputs.models.map((model, i) => {
                                                    return (
                                                        <tr
                                                            key={i}
                                                            onMouseOver={() =>
                                                                store.setHoverModel(model)
                                                            }
                                                            onMouseOut={() =>
                                                                store.setHoverModel(null)
                                                            }
                                                            className={
                                                                selected_model_index === i
                                                                    ? "table-info"
                                                                    : ""
                                                            }>
                                                            <td>{model.name}</td>
                                                            <td>{h.ff(model.results.bmdl)}</td>
                                                            <td>{h.ff(model.results.bmd)}</td>
                                                            <td>{h.ff(model.results.bmdu)}</td>
                                                            <td>
                                                                {h.ff(
                                                                    model.results.gof.p_value ||
                                                                        model.results.tests
                                                                            .p_values[3]
                                                                )}
                                                            </td>
                                                            <td>{h.ff(model.results.fit.aic)}</td>
                                                            <td>{h.ff(model.results.gof.roi)}</td>
                                                            <td>
                                                                {h.ff(
                                                                    model.results.gof.residual[0]
                                                                )}
                                                            </td>
                                                            <td>TODO.</td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                        <p className="text-muted">
                                            {store.bmrText}
                                            {store.variableModelText
                                                ? `; ${store.variableModelText} Variance`
                                                : ""}
                                        </p>
                                    </div>
                                    <div className="col-xl-4">
                                        <h3>Summary Figure</h3>
                                        <OutputFigure
                                            endpoint={endpoint}
                                            hoverModel={toJS(store.hoverModel)}
                                            selectedModel={store.selectedModel}
                                        />
                                    </div>
                                </div>
                                <div className="row">
                                    {readOnly ? null : (
                                        <div className="col-md-12">
                                            <div className="row">
                                                <div className="col-md-4">
                                                    <SelectInput
                                                        choices={store.selectedChoices}
                                                        handleSelect={value =>
                                                            store.changeSelectedModel(
                                                                parseInt(value)
                                                            )
                                                        }
                                                        value={selected.model_index.toString()}
                                                        label="Selected best-fitting model"
                                                        helpText="..."
                                                    />
                                                </div>
                                                <div className="col-md-4">
                                                    <TextAreaInput
                                                        name="model_selection"
                                                        label="Selection notes"
                                                        value={selected.notes}
                                                        onChange={e =>
                                                            store.changeSelectedNotes(
                                                                e.target.value
                                                            )
                                                        }
                                                        helpText="..."
                                                    />
                                                </div>
                                                <div className="col-md-4">
                                                    <label>&nbsp;</label>
                                                    <button
                                                        className="btn btn-primary btn-block"
                                                        onClick={store.handleSelectionSave}>
                                                        Save model selection
                                                    </button>
                                                    {store.showSelectedSaveNotification ? (
                                                        <div className="alert alert-success text-center mt-2">
                                                            <i className="fa fa-fw fa-check"></i>
                                                            &nbsp;Save successful!
                                                        </div>
                                                    ) : null}
                                                    {store.selectedError ? (
                                                        <div className="alert alert-danger text-center mt-2">
                                                            <i className="fa fa-fw fa-exclamation-triangle"></i>
                                                            &nbsp;An error occurred
                                                        </div>
                                                    ) : null}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : null}
                        {!store.hasErrors && !store.hasOutputs ? (
                            <div>
                                <div className="row">
                                    <div className="col-md-12">
                                        <p className="text-muted">Analysis not yet executed.</p>
                                    </div>
                                </div>
                            </div>
                        ) : null}
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
