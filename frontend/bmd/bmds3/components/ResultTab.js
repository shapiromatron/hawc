import _ from "lodash";
import {toJS} from "mobx";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import Alert from "shared/components/Alert";
import SelectInput from "shared/components/SelectInput";
import TextAreaInput from "shared/components/TextAreaInput";
import h from "shared/utils/helpers";

import OutputFigure from "../../bmds2/components/OutputFigure";
import ModelModal from "./ModelModal";

const RecommendationTd = function({bin, notes}) {
    const label = {0: "Viable", 1: "Questionable", 2: "Unusable"};
    return (
        <td>
            <u>{label[bin]}</u>
            <ul className="list-unstyled text-muted mb-0">
                {_.flatten([notes[2], notes[1], notes[0]]).map((d, idx) => (
                    <li key={idx}>{d}</li>
                ))}
            </ul>
        </td>
    );
};
RecommendationTd.propTypes = {
    bin: PropTypes.number.isRequired,
    notes: PropTypes.object.isRequired,
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
                    <col width="10%" />
                    <col width="10%" />
                    <col width="25%" />
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
                        <th>Recommendation and Notes</th>
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
                                <td>{h.ff(model.results.bmdl)}</td>
                                <td>{h.ff(model.results.bmd)}</td>
                                <td>{h.ff(model.results.bmdu)}</td>
                                <td>
                                    {h.ff(
                                        model.results.gof.p_value || model.results.tests.p_values[3]
                                    )}
                                </td>
                                <td>{h.ff(model.results.fit.aic)}</td>
                                <td>{h.ff(model.results.gof.roi)}</td>
                                <td>{h.ff(model.results.gof.residual[0])}</td>
                                <RecommendationTd
                                    bin={store.outputs.recommender.results.model_bin[i]}
                                    notes={store.outputs.recommender.results.model_notes[i]}
                                />
                            </tr>
                        );
                    })}
                </tbody>
                <tfoot>
                    <tr>
                        <td colSpan={9}>
                            <p className="text-sm m-0">{store.bmrText}</p>
                            {store.variableModelText ? (
                                <p className="text-sm m-0">
                                    Variance Model {store.variableModelText}
                                </p>
                            ) : null}
                            {selected_model_index >= 0 ? (
                                <p className="text-sm m-0">* Selected model</p>
                            ) : null}
                            {selected_model_index < 0 && recommended_model_index >= 0 ? (
                                <p className="text-sm m-0">† Recommended model</p>
                            ) : null}
                            <p className="text-sm m-0">pybmds version {store.pybmdsVersion}</p>
                            <p className="text-sm m-0">Execution date {store.executionDate}</p>
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
            {endpoint} = store;

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
                    <div className="col-xl-8">
                        <h3>Summary Table</h3>
                        <SummaryTable />
                        <ModelSelection />
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
                <ModelModal />
            </div>
        );
    }
}
ResultTab.propTypes = {
    store: PropTypes.object,
};

export default ResultTab;