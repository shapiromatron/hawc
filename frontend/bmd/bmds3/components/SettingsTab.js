import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import Alert from "shared/components/Alert";
import FloatInput from "shared/components/FloatInput";
import SelectInput from "shared/components/SelectInput";
import WaitLoad from "shared/components/WaitLoad";
import {
    ActionsTh,
    MoveRowTd,
    moveArrayElementDown,
    moveArrayElementUp,
    EditableRow,
    deleteArrayElement,
} from "shared/components/EditableRowData";
import HelpTextPopup from "shared/components/HelpTextPopup";
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
            <>
                <DatasetTable withResults={false} />,
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
            </>
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
class OptionSetRow extends EditableRow {
    renderViewRow(row, index) {
        // const {deleteArrayElement, sectionMapping} = this.props.store.subclass;
        return (
            <tr>
                <td>VIEW</td>
            </tr>
        );
    }
    renderEditRow(row, index) {
        const {store} = this.props,
            {
                bmrTypeChoices,
                varianceModelChoices,
                changeSetting,
                doseDropChoices,
                isContinuous,
                inputs,
            } = store;
        return (
            <tr>
                <td>
                    <SelectInput
                        choices={doseDropChoices}
                        name={`settings.${index}.num_doses_dropped`}
                        handleSelect={value =>
                            changeSetting(`settings.${index}.num_doses_dropped`, parseInt(value))
                        }
                        value={row.num_doses_dropped.toString()}
                    />
                </td>
                <td>
                    <SelectInput
                        choices={bmrTypeChoices}
                        name={`settings.${index}.bmr_type`}
                        handleSelect={value =>
                            changeSetting(`settings.${index}.bmr_type`, parseInt(value))
                        }
                        value={row.bmr_type.toString()}
                    />
                </td>
                <td>
                    <FloatInput
                        name={`settings.${index}.bmr_value`}
                        value={row.bmr_value}
                        onChange={e =>
                            changeSetting(`settings.${index}.bmr_value`, parseFloat(e.target.value))
                        }
                    />
                </td>
                <td>
                    {isContinuous ? (
                        <SelectInput
                            name={`settings.${index}.variance_model`}
                            choices={varianceModelChoices}
                            handleSelect={value =>
                                changeSetting(`settings.${index}.variance_model`, parseInt(value))
                            }
                            value={row.variance_model.toString()}
                        />
                    ) : null}
                </td>
                <MoveRowTd
                    onMoveUp={() => moveArrayElementUp(inputs.settings, index)}
                    onMoveDown={() => moveArrayElementDown(inputs.settings, index)}
                    onDelete={
                        index > 0 ? () => deleteArrayElement(inputs.settings, index) : undefined
                    }
                />
            </tr>
        );
    }
}

@inject("store")
@observer
class SettingsForm extends React.Component {
    render() {
        const {store} = this.props,
            {
                doseUnitChoices,
                inputs,
                changeSetting,
                executionError,
                isContinuous,
                createSettingsRow,
            } = store;

        return (
            <>
                <div className="row">
                    <div className="col-md-6">
                        <SelectInput
                            choices={doseUnitChoices}
                            handleSelect={value => changeSetting("dose_units_id", parseInt(value))}
                            value={inputs.dose_units_id.toString()}
                            label="Dose Units"
                            helpText="Select which dose units to use for modeling. You can create different sessions with different dose units."
                        />
                    </div>
                </div>
                <div className="row">
                    <DatasetTable withResults={false} />
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <p className="mb-1 h3">Option Sets</p>
                        <table className="table table-sm table-striped">
                            <colgroup>
                                <col width="20%" />
                                <col width="25%" />
                                <col width="15%" />
                                {isContinuous ? <col width="25%" /> : null}
                                <col width="15%" />
                            </colgroup>
                            <thead>
                                <tr>
                                    <th>
                                        Doses to Drop
                                        <HelpTextPopup
                                            content={"Benchmark response type."}
                                            title={
                                                "Remove dose groups from modeling; the highest groups are removed."
                                            }
                                        />
                                    </th>
                                    <th>
                                        BMR Type
                                        <HelpTextPopup
                                            content={"Benchmark response type."}
                                            title={"BMR Type"}
                                        />
                                    </th>
                                    <th>
                                        BMR Value
                                        <HelpTextPopup
                                            content={"Benchmark response value."}
                                            title={"BMR"}
                                        />
                                    </th>
                                    {isContinuous ? (
                                        <th>
                                            Variance Model
                                            <HelpTextPopup
                                                content={"Which variance model to use."}
                                                title={"Variance Model"}
                                            />
                                        </th>
                                    ) : null}
                                    <ActionsTh onClickNew={createSettingsRow} />
                                </tr>
                            </thead>
                            <tbody>
                                {inputs.settings.map((row, index) => {
                                    const key = `${index}-${JSON.stringify(row)}`;
                                    return (
                                        <OptionSetRow
                                            row={row}
                                            index={index}
                                            key={key}
                                            initiallyEditable={true}
                                        />
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div className="row">
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
            </>
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
