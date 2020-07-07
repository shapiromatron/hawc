import React from "react";
import {connect} from "react-redux";
import PropTypes from "prop-types";

import ModelOptionModal from "bmd/components/ModelOptionModal";
import BMROptionModal from "bmd/components/BMROptionModal";
import OutputModal from "bmd/components/OutputModal";

import {updateModel, deleteModel, updateBmr, deleteBmr} from "bmd/actions";

class Modals extends React.Component {
    handleModelUpdate(values) {
        this.props.dispatch(updateModel(values));
    }

    handleModelDelete() {
        this.props.dispatch(deleteModel());
    }

    handleBmrUpdate(values) {
        this.props.dispatch(updateBmr(values));
    }

    handleBmrDelete() {
        this.props.dispatch(deleteBmr());
    }

    isReady() {
        return this.props.allBmrOptions !== null;
    }

    render() {
        if (!this.isReady()) {
            return null;
        }
        let {editMode} = this.props.config;
        return (
            <div>
                <ModelOptionModal
                    model={this.props.selectedModelOption}
                    editMode={editMode}
                    handleSave={this.handleModelUpdate.bind(this)}
                    handleDelete={this.handleModelDelete.bind(this)}
                />
                <BMROptionModal
                    bmr={this.props.selectedBmr}
                    allOptions={this.props.allBmrOptions}
                    editMode={editMode}
                    handleSave={this.handleBmrUpdate.bind(this)}
                    handleDelete={this.handleBmrDelete.bind(this)}
                />
                <OutputModal models={this.props.selectedOutputs} />
            </div>
        );
    }
}

function mapStateToProps(state) {
    return {
        config: state.config,
        selectedModelOption: state.bmd.selectedModelOption,
        selectedBmr: state.bmd.selectedBmr,
        allBmrOptions: state.bmd.allBmrOptions,
        selectedOutputs: state.bmd.selectedOutputs,
    };
}

Modals.propTypes = {
    dispatch: PropTypes.object,
    allBmrOptions: PropTypes.object,
    config: PropTypes.shape({
        editMode: PropTypes.object,
    }),
    selectedModelOption: PropTypes.object,
    selectedBmr: PropTypes.object,
    selectedOutputs: PropTypes.object,
};
export default connect(mapStateToProps)(Modals);
