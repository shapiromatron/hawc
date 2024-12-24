import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import Alert from "shared/components/Alert";
import SelectInput from "shared/components/SelectInput";
import TextAreaInput from "shared/components/TextAreaInput";
import WaitLoad from "shared/components/WaitLoad";

import {ff, fractionalFormatter} from "../formatters";
import DatasetTable from "./DatasetTable";
import DoseResponsePlot from "./DoseResponsePlot";
import ModelModal from "./ModelModal";
import {SettingsTable} from "./SettingsTab";

const RecommendationTd = function({results, model_index}) {
    const bin = results.model_bin[model_index],
        notes = results.model_notes[model_index],
        label = {
            0: "Viable",
            1: "Questionable",
            2: "Unusable",
            aic: "Recommended - Lowest AIC",
            bmdl: "Recommended - Lowest BMDL",
        };
    return (
        <td>
            <u>
                {model_index === results.recommended_model_index
                    ? label[results.recommended_model_variable]
                    : label[bin]}
            </u>
            <ul className="list-unstyled text-muted mb-0">
                {_.flatten([notes[2], notes[1], notes[0]]).map((d, idx) => (
                    <li key={idx}>{d}</li>
                ))}
            </ul>
        </td>
    );
};
RecommendationTd.propTypes = {
    results: PropTypes.object.isRequired,
    model_index: PropTypes.number.isRequired,
};

@inject("store")
@observer
class ModelSelection extends React.Component {
    render() {
        const {store} = this.props,
            readOnly = !store.config.edit,
            {selected} = store;
        if (readOnly) {
            return null;
        }
        return (
            <div className="row well">
                <div className="col-md-7">
                    <SelectInput
                        choices={store.selectedChoices}
                        handleSelect={value => store.changeSelectedModel(parseInt(value))}
                        value={selected.model_index.toString()}
                        label="Selected best-fitting model"
                    />
                    <TextAreaInput
                        name="model_selection"
                        label="Selection notes"
                        value={selected.notes}
                        onChange={e => store.changeSelectedNotes(e.target.value)}
                    />
                </div>
                <div className="col-md-5">
                    <label>&nbsp;</label>
                    <button
                        className="btn btn-primary btn-block"
                        onClick={store.handleSelectionSave}>
                        Save model selection
                    </button>
                    {store.showSelectedSaveNotification ? (
                        <Alert
                            className="alert-success"
                            icon="fa-check"
                            message="Save successful!"
                            testId="select-model-confirmation"
                        />
                    ) : null}
                    {store.selectedError ? <Alert /> : null}
                </div>
            </div>
        );
    }
}
ModelSelection.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class SummaryTable extends React.Component {
    render() {
        const {store} = this.props,
            {recommended_model_index} = store.outputs.recommender.results,
            selected_model_index = store.selected.model_index,
            getRowClass = i => {
                if (selected_model_index === i) {
                    return "table-info";
                } else if (selected_model_index < 0 && recommended_model_index === i) {
                    return "table-warning";
                } else {
                    return "";
                }
            };
        return (
            <table className="table table-sm table-striped table-hover text-right col-l-1">
                <colgroup>
                    <col width="15%" />
                    <col width="8%" />
                    <col width="8%" />
                    <col width="8%" />
                    <col width="8%" />
                    <col width="8%" />
                    <col width="11%" />
                    <col width="11%" />
                    <col width="23%" />
                </colgroup>
                <thead>
                    <tr>
                        <th>Model Name</th>
                        <th>BMDL</th>
                        <th>BMD</th>
                        <th>BMDU</th>
                        <th>
                            <i>P</i>-Value
                        </th>
                        <th>AIC</th>
                        <th>Scaled Residual at Control</th>
                        <th>Scaled Residual near BMD</th>
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
                                onMouseOver={() => store.setHoverModel(model)}
                                onMouseOut={() => store.setHoverModel(null)}
                                className={getRowClass(i)}>
                                <td>
                                    <button
                                        className="btn btn-link text-left m-0 p-0"
                                        onClick={() => store.enableModal(model)}>
                                        {model.name}
                                        {selected_model_index === i ? <sup>*</sup> : ""}
                                        {recommended_model_index === i ? <sup>†</sup> : ""}
                                    </button>
                                </td>
                                <td>{ff(model.results.bmdl)}</td>
                                <td>{ff(model.results.bmd)}</td>
                                <td>{ff(model.results.bmdu)}</td>
                                <td>
                                    {fractionalFormatter(
                                        model.results.gof.p_value || model.results.tests.p_values[3]
                                    )}
                                </td>
                                <td>{ff(model.results.fit.aic)}</td>
                                <td>{ff(model.results.gof.residual[0])}</td>
                                <td>{ff(model.results.gof.roi)}</td>
                                <RecommendationTd
                                    results={store.outputs.recommender.results}
                                    model_index={i}
                                />
                            </tr>
                        );
                    })}
                </tbody>
                <tfoot>
                    <tr>
                        <td colSpan={9}>
                            {selected_model_index >= 0 ? (
                                <p className="text-sm m-0">* Selected model</p>
                            ) : null}
                            {selected_model_index < 0 && recommended_model_index >= 0 ? (
                                <p className="text-sm m-0">† Recommended model</p>
                            ) : null}
                        </td>
                    </tr>
                </tfoot>
            </table>
        );
    }
}
SummaryTable.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class ResultTab extends React.Component {
    render() {
        const {store} = this.props,
            readOnly = !store.config.edit;

        if (store.hasErrors) {
            return (
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-md-12">
                            <h3>Execution Error</h3>
                            <Alert
                                className="alert-danger"
                                icon="fa-exclamation-triangle"
                                message="An error occurred. Please contact HAWC developers if this continues to occur."
                            />
                        </div>
                    </div>
                </div>
            );
        }

        if (!store.hasOutputs) {
            return (
                <div className="container-fluid">
                    <div className="row">
                        <div className="col-md-12">
                            <Alert
                                className="alert-info"
                                icon="fa-exclamation-circle"
                                message="Analysis not yet executed."
                            />
                        </div>
                    </div>
                </div>
            );
        }

        return (
            <div className="container-fluid">
                <div className="row">
                    <div className="col-lg-5">
                        <h3>Settings</h3>
                        <SettingsTable showRunMetadata={true} />
                        <h3>Dataset</h3>
                        <DatasetTable withResults={true} />
                    </div>
                    <div className="col-lg-7 d-flex align-items-end justify-content-center">
                        <div style={{height: "400px"}}>
                            <WaitLoad>
                                <DoseResponsePlot
                                    showDataset={true}
                                    showSelected={true}
                                    showHover={true}
                                />
                            </WaitLoad>
                        </div>
                    </div>
                    <div className="col-lg-12 pt-3">
                        <h3>Model Results</h3>
                        <SummaryTable />
                        {!readOnly ? <h3>Model Selection</h3> : null}
                        <ModelSelection />
                    </div>
                </div>
                <ModelModal />
            </div>
        );
    }
}
ResultTab.propTypes = {
    store: PropTypes.object,
};

export default ResultTab;
