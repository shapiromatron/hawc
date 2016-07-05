import React from 'react';
import { connect } from 'react-redux';
import $ from '$';

import Loading from 'shared/components/Loading';

import DoseResponse from 'bmd/components/DoseResponse';
import ModelOptionTable from 'bmd/components/ModelOptionTable';
import BMROptionTable from 'bmd/components/BMROptionTable';
import ExecuteWell from 'bmd/components/ExecuteWell';
import RecommendationTable from 'bmd/components/RecommendationTable';
import OutputTable from 'bmd/components/OutputTable';

import {
    fetchEndpoint,
    fetchSessionSettings,
    showOptionModal,
    execute,
    toggleVariance,
    createModel,
    createBmr,
    saveSelected,
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
        this.props.dispatch(execute());
    }

    handleVarianceToggle(){
        this.props.dispatch(toggleVariance());
    }

    handleCreateModel(modelName){
        this.props.dispatch(createModel(modelName));
    }

    handleModalDisplay(modelIndex){
        this.props.dispatch(showOptionModal(modelIndex));
    }

    handleCreateBmr(){
        this.props.dispatch(createBmr());
    }

    handleSaveSelected(){
        this.props.dispatch(saveSelected());
    }

    isReady(){
        return (this.props.endpoint !== null);
    }

    render(){
        let {editMode, bmds_version} = this.props.config,
            {endpoint, dataType} = this.props,
            showResultsTabs = (editMode)?'':'disabled';  // todo - only show if results available

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
                                handleCreateModel={this.handleCreateModel.bind(this)}
                                handleModalDisplay={this.handleModalDisplay.bind(this)}
                                models={this.props.models}
                                allOptions={this.props.allModelOptions}/>
                            <BMROptionTable
                                editMode={editMode}
                                handleCreateBmr={this.handleCreateBmr.bind(this)}/>
                        </div>
                        <ExecuteWell
                            editMode={editMode}
                            handleExecute={this.handleExecute.bind(this)} />
                    </div>
                    <div id="results" className="tab-pane">
                        <OutputTable />
                    </div>
                    <div id="recommendations" className="tab-pane">
                        <RecommendationTable
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
        models: state.bmd.models,
        allModelOptions: state.bmd.allModelOptions,
    };
}

export default connect(mapStateToProps)(Tabs);

