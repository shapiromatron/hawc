import React from 'react';
import { connect } from 'react-redux';
import $ from '$';

import Loading from 'shared/components/Loading';

import DoseResponse from 'bmd/components/DoseResponse';
import ModelOptionTable from 'bmd/components/ModelOptionTable';
import BMROptionTable from 'bmd/components/BMROptionTable';
import ExecuteWell from 'bmd/components/ExecuteWell';
import Recommendation from 'bmd/components/Recommendation';
import OutputTable from 'bmd/components/OutputTable';
import OutputFigure from 'bmd/components/OutputFigure';


import {
    fetchEndpoint,
    fetchSessionSettings,
    showOptionModal,
    showBmrModal,
    showOutputModal,
    setHoverModel,
    tryExecute,
    toggleVariance,
    addAllModels,
    removeAllModels,
    createModel,
    createBmr,
    saveSelectedModel,
} from 'bmd/actions';


class Tabs extends React.Component {

    componentWillMount(){
        this.props.dispatch(fetchEndpoint(this.props.config.endpoint_id));
        this.props.dispatch(fetchSessionSettings(this.props.config.session_url));
    }

    componentDidUpdate(){
        if ($('.tab-pane.active').length === 0){
            $('#tabs a:first').tab('show');
        }
    }

    handleTabClick(event){
        let tabDisabled = $(event.currentTarget.parentElement).hasClass('disabled');
        if (!tabDisabled){
            $(event.currentTarget).tab('show');
        }
    }

    handleExecute(){
        this.props.dispatch(tryExecute());
    }

    handleVarianceToggle(evt){
        evt.preventDefault();
        this.props.dispatch(toggleVariance());
    }

    handleAddAll(evt){
        evt.preventDefault();
        this.props.dispatch(addAllModels());
    }

    handleRemoveAll(evt){
        evt.preventDefault();
        this.props.dispatch(removeAllModels());
    }

    handleCreateModel(modelName){
        this.props.dispatch(createModel(modelName));
    }

    handleOptionModal(modelIndex){
        this.props.dispatch(showOptionModal(modelIndex));
    }

    handleBmrModal(bmrIndex){
        this.props.dispatch(showBmrModal(bmrIndex));
    }

    handleCreateBmr(){
        this.props.dispatch(createBmr());
    }

    handleSaveSelected(model_id, notes){
        this.props.dispatch(saveSelectedModel(model_id, notes));
    }

    handleOutputModal(model){
        this.props.dispatch(showOutputModal(model));
    }

    handleModelHover(model){
        this.props.dispatch(setHoverModel(model));
    }

    handleModelNoHover(){
        this.props.dispatch(setHoverModel(null));
    }

    isReady(){
        return (this.props.endpoint !== null);
    }

    render(){
        let {editMode, bmds_version} = this.props.config,
            {
                bmrs, endpoint, dataType, models, selectedModelId,
                selectedModelNotes, validationErrors, isExecuting, hoverModel,
            } = this.props,
            showResultsTabs = (models.length>0)?'':'disabled';  // todo - only show if results available

        if (!this.isReady()){
            return <Loading />;
        }

        return (
            <div>
                <div className="row-fluid">
                    <ul className="nav nav-tabs" id="tabs">
                        <li><a href="#setup"
                            onClick={this.handleTabClick}>BMD setup</a></li>
                        <li className={showResultsTabs}><a href="#results"
                            onClick={this.handleTabClick}>Results</a></li>
                        <li className={showResultsTabs}><a href="#recommendations"
                            onClick={this.handleTabClick}>Recommendation and selection</a></li>
                    </ul>
                </div>

                <div className="tab-content">
                    <div id="setup" className="tab-pane">
                        <DoseResponse endpoint={endpoint} />
                        <h3>Selected models and options</h3>
                        <p>
                            <i>BMDS version: {bmds_version}</i>
                        </p>
                        <div className="row-fluid">
                            <ModelOptionTable
                                editMode={editMode}
                                dataType={dataType}
                                handleVarianceToggle={this.handleVarianceToggle.bind(this)}
                                handleAddAll={this.handleAddAll.bind(this)}
                                handleRemoveAll={this.handleRemoveAll.bind(this)}
                                handleCreateModel={this.handleCreateModel.bind(this)}
                                handleModalDisplay={this.handleOptionModal.bind(this)}
                                models={this.props.modelSettings}
                                allOptions={this.props.allModelOptions}/>
                            <BMROptionTable
                                editMode={editMode}
                                handleCreateBmr={this.handleCreateBmr.bind(this)}
                                handleModalDisplay={this.handleBmrModal.bind(this)}
                                bmrs={this.props.bmrs}/>
                        </div>
                        <ExecuteWell
                            editMode={editMode}
                            validationErrors={validationErrors}
                            isExecuting={isExecuting}
                            handleExecute={this.handleExecute.bind(this)} />
                    </div>
                    <div id="results" className="tab-pane">
                        <h3>BMDS output summary</h3>
                        <div className="row-fluid">
                            <OutputTable
                                models={models}
                                bmrs={bmrs}
                                handleModal={this.handleOutputModal.bind(this)}
                                handleModelHover={this.handleModelHover.bind(this)}
                                handleModelNoHover={this.handleModelNoHover.bind(this)}/>
                            <OutputFigure
                                endpoint={endpoint}
                                hoverModel={hoverModel} />
                        </div>
                    </div>
                    <div id="recommendations" className="tab-pane">
                        <Recommendation
                            models={models}
                            bmrs={bmrs}
                            selectedModelId={selectedModelId}
                            selectedModelNotes={selectedModelNotes}
                            handleSaveSelected={this.handleSaveSelected.bind(this)}/>
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
        dataType: state.bmd.dataType,
        modelSettings: state.bmd.modelSettings,
        models: state.bmd.models,
        bmrs: state.bmd.bmrs,
        allModelOptions: state.bmd.allModelOptions,
        allBmrOptions: state.bmd.allBmrOptions,
        validationErrors: state.bmd.validationErrors,
        isExecuting: state.bmd.isExecuting,
        hoverModel: state.bmd.hoverModel,
        selectedModelId: state.bmd.selectedModelId,
        selectedModelNotes: state.bmd.selectedModelNotes,
    };
}

export default connect(mapStateToProps)(Tabs);

