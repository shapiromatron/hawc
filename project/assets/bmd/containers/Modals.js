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

    handleModelUpdate(){
        this.props.dispatch(updateModel());
    }

    handleModelDelete(){
        this.props.dispatch(deleteModel());
    }

    handleBmrUpdate(){
        this.props.dispatch(updateBmr());
    }

    handleBmrDelete(){
        this.props.dispatch(deleteBmr());
    }

    render() {
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
    };
}

export default connect(mapStateToProps)(Modals);

