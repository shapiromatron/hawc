import React from "react";
import {connect} from "react-redux";
import _ from "lodash";
import $ from "$";
import PropTypes from "prop-types";

import Loading from "shared/components/Loading";

import DoseResponse from "bmd/components/DoseResponse";
import DoseUnitsSelector from "bmd/components/DoseUnitsSelector";
import ModelOptionTable from "bmd/components/ModelOptionTable";
import BMROptionTable from "bmd/components/BMROptionTable";
import ExecuteWell from "bmd/components/ExecuteWell";
import Recommendation from "bmd/components/Recommendation";
import RecommendationNotes from "bmd/components/RecommendationNotes";
import OutputTable from "bmd/components/OutputTable";
import OutputFigure from "bmd/components/OutputFigure";

import {
    fetchEndpoint,
    fetchSessionSettings,
    showOptionModal,
    showBmrModal,
    showOutputModal,
    changeUnits,
    setHoverModel,
    tryExecute,
    toggleVariance,
    addAllModels,
    removeAllModels,
    createModel,
    createBmr,
    saveSelectedModel,
    applyLogic,
} from "bmd/actions";

class Tabs extends React.Component {
    constructor(props) {
        super(props);
        this.props.dispatch(fetchEndpoint(props.config.endpoint_id));
        this.props.dispatch(fetchSessionSettings(props.config.session_url));
    }

    componentDidUpdate() {
        if ($(".tab-pane.active").length === 0) {
            $("#tabs a:first").tab("show");
        }
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        if (nextProps.logicApplied === false && nextProps.hasSession && nextProps.hasEndpoint) {
            this.props.dispatch(applyLogic());
        }
    }

    handleTabClick(event) {
        let tabDisabled = $(event.currentTarget.parentElement).hasClass("disabled");
        if (!tabDisabled) {
            $(event.currentTarget).tab("show");
        }
    }

    handleUnitsChange(doseUnits) {
        this.props.dispatch(changeUnits(doseUnits));
    }

    handleExecute() {
        this.props.dispatch(tryExecute());
    }

    handleVarianceToggle(evt) {
        evt.preventDefault();
        this.props.dispatch(toggleVariance());
    }

    handleAddAll(evt) {
        evt.preventDefault();
        this.props.dispatch(addAllModels());
    }

    handleRemoveAll(evt) {
        evt.preventDefault();
        this.props.dispatch(removeAllModels());
    }

    handleCreateModel(modelName) {
        this.props.dispatch(createModel(modelName));
    }

    handleOptionModal(modelIndex) {
        this.props.dispatch(showOptionModal(modelIndex));
    }

    handleBmrModal(bmrIndex) {
        this.props.dispatch(showBmrModal(bmrIndex));
    }

    handleCreateBmr() {
        this.props.dispatch(createBmr());
    }

    handleSaveSelected(model_id, notes) {
        this.props.dispatch(saveSelectedModel(model_id, notes));
    }

    handleOutputModal(models) {
        this.props.dispatch(showOutputModal(models));
    }

    handleModelHover(model) {
        this.props.dispatch(setHoverModel(model));
    }

    handleModelNoHover() {
        this.props.dispatch(setHoverModel(null));
    }

    renderSetupTab() {
        let {editMode, bmds_version} = this.props.config,
            {endpoint, dataType, validationErrors, isExecuting, doseUnits} = this.props;

        return (
            <div>
                <DoseResponse endpoint={endpoint} />
                <h3>Selected models and options</h3>
                <DoseUnitsSelector
                    version={bmds_version}
                    editMode={editMode}
                    endpoint={endpoint}
                    doseUnits={doseUnits}
                    handleUnitsChange={this.handleUnitsChange.bind(this)}
                />
                <div className="row">
                    <ModelOptionTable
                        editMode={editMode}
                        dataType={dataType}
                        handleVarianceToggle={this.handleVarianceToggle.bind(this)}
                        handleAddAll={this.handleAddAll.bind(this)}
                        handleRemoveAll={this.handleRemoveAll.bind(this)}
                        handleCreateModel={this.handleCreateModel.bind(this)}
                        handleModalDisplay={this.handleOptionModal.bind(this)}
                        models={this.props.modelSettings}
                        allOptions={this.props.allModelOptions}
                    />
                    <BMROptionTable
                        editMode={editMode}
                        handleCreateBmr={this.handleCreateBmr.bind(this)}
                        handleModalDisplay={this.handleBmrModal.bind(this)}
                        bmrs={this.props.bmrs}
                    />
                </div>
                <ExecuteWell
                    editMode={editMode}
                    validationErrors={validationErrors}
                    isExecuting={isExecuting}
                    handleExecute={this.handleExecute.bind(this)}
                />
            </div>
        );
    }

    renderResultsTab() {
        let {bmrs, endpoint, models, selectedModelId, hoverModel, hasExecuted} = this.props,
            selectedModel = _.find(models, {id: selectedModelId}) || null;

        if (!hasExecuted) {
            return null;
        }

        return [
            <h3 key={0}>BMDS output summary</h3>,
            <div key={1} className="row">
                <OutputTable
                    models={models}
                    bmrs={bmrs}
                    handleModal={this.handleOutputModal.bind(this)}
                    handleModelHover={this.handleModelHover.bind(this)}
                    handleModelNoHover={this.handleModelNoHover.bind(this)}
                    selectedModelId={selectedModelId}
                />
                <OutputFigure
                    endpoint={endpoint}
                    hoverModel={hoverModel}
                    selectedModel={selectedModel}
                />
            </div>,
            <RecommendationNotes key={2} notes={this.props.selectedModelNotes} />,
        ];
    }

    renderRecommendationTab() {
        let {editMode} = this.props.config,
            {bmrs, models, selectedModelId, selectedModelNotes, hasExecuted} = this.props;

        if (!hasExecuted) {
            return null;
        }

        return (
            <Recommendation
                editMode={editMode}
                models={models}
                bmrs={bmrs}
                selectedModelId={selectedModelId}
                selectedModelNotes={selectedModelNotes}
                handleSaveSelected={this.handleSaveSelected.bind(this)}
            />
        );
    }

    render() {
        let {hasExecuted} = this.props,
            showResultsTabs = hasExecuted ? "" : "disabled";

        if (this.props.logicApplied === false) {
            return <Loading />;
        }

        return (
            <div>
                <div className="row">
                    <ul className="nav nav-tabs" id="tabs">
                        <li>
                            <a href="#setup" onClick={this.handleTabClick}>
                                BMD setup
                            </a>
                        </li>
                        <li className={showResultsTabs}>
                            <a href="#results" onClick={this.handleTabClick}>
                                Results
                            </a>
                        </li>
                        <li className={showResultsTabs}>
                            <a href="#recommendations" onClick={this.handleTabClick}>
                                Model recommendation and selection
                            </a>
                        </li>
                    </ul>
                </div>

                <div className="tab-content">
                    <div id="setup" className="tab-pane">
                        {this.renderSetupTab()}
                    </div>
                    <div id="results" className="tab-pane">
                        {this.renderResultsTab()}
                    </div>
                    <div id="recommendations" className="tab-pane">
                        {this.renderRecommendationTab()}
                    </div>
                </div>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        config: state.config,
        endpoint: state.bmd.endpoint,
        doseUnits: state.bmd.doseUnits,
        dataType: state.bmd.dataType,
        modelSettings: state.bmd.modelSettings,
        models: state.bmd.models,
        bmrs: state.bmd.bmrs,
        allModelOptions: state.bmd.allModelOptions,
        allBmrOptions: state.bmd.allBmrOptions,
        validationErrors: state.bmd.validationErrors,
        isExecuting: state.bmd.isExecuting,
        hasExecuted: state.bmd.hasExecuted,
        hoverModel: state.bmd.hoverModel,
        selectedModelId: state.bmd.selectedModelId,
        selectedModelNotes: state.bmd.selectedModelNotes,
        hasSession: state.bmd.hasSession,
        hasEndpoint: state.bmd.hasEndpoint,
        logicApplied: state.bmd.logicApplied,
    };
}

Tabs.propTypes = {
    dispatch: PropTypes.func,
    config: PropTypes.shape({
        endpoint_id: PropTypes.number,
        session_url: PropTypes.string,
        editMode: PropTypes.bool,
        bmds_version: PropTypes.string,
    }),
    logicApplied: PropTypes.bool,
    hasSession: PropTypes.bool,
    hasEndpoint: PropTypes.bool,
    endpoint: PropTypes.object,
    dataType: PropTypes.string,
    validationErrors: PropTypes.array,
    isExecuting: PropTypes.bool,
    doseUnits: PropTypes.number,
    modelSettings: PropTypes.array,
    allModelOptions: PropTypes.array,
    bmrs: PropTypes.array,
    models: PropTypes.array,
    selectedModelId: PropTypes.number,
    hoverModel: PropTypes.object,
    hasExecuted: PropTypes.bool,
    selectedModelNotes: PropTypes.string,
};
export default connect(mapStateToProps)(Tabs);
