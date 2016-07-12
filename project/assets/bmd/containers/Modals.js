import React from 'react';
import { connect } from 'react-redux';

import ModelOptionModal from 'bmd/components/ModelOptionModal';
import BMROptionModal from 'bmd/components/BMROptionModal';
import OutputModal from 'bmd/components/OutputModal';

import {
    showOutputModal,
    updateModel,
    deleteModel,
    updateBmr,
    deleteBmr,
} from 'bmd/actions';


class Modals extends React.Component {

    handleOutputClick(){
        this.props.dispatch(showOutputModal);
    }

    handleModelUpdate(values){
        this.props.dispatch(updateModel(values));
    }

    handleModelDelete(){
        this.props.dispatch(deleteModel());
    }

    handleBmrUpdate(values){
        this.props.dispatch(updateBmr(values));
    }

    handleBmrDelete(){
        this.props.dispatch(deleteBmr());
    }

    isReady(){
        return (this.props.allBmrOptions !== null);
    }

    render() {
        if (!this.isReady()){
            return null;
        }
        let {editMode} = this.props.config;
        return (
            <div>
                <ModelOptionModal
                    model={this.props.selectedModel}
                    editMode={editMode}
                    handleSave={this.handleModelUpdate.bind(this)}
                    handleDelete={this.handleModelDelete.bind(this)}/>
                <BMROptionModal
                    bmr={this.props.selectedBmr}
                    allOptions={this.props.allBmrOptions}
                    editMode={editMode}
                    handleSave={this.handleBmrUpdate.bind(this)}
                    handleDelete={this.handleBmrDelete.bind(this)} />
                <OutputModal />

                <button type='button'
                    onClick={this.handleOutputClick.bind(this)}>Output</button>
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        config: state.config,
        selectedModel: state.bmd.selectedModel,
        selectedBmr: state.bmd.selectedBmr,
        allBmrOptions: state.bmd.allBmrOptions,
    };
}

export default connect(mapStateToProps)(Modals);

