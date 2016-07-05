import React from 'react';

import * as types from 'bmd/constants';

import EditableModalFooter from 'bmd/components/EditableModalFooter';


class ModelOptionModal extends React.Component {

    renderReadOnly(){
        return (
            <div className="modal-body">
                <div className='row-fluid'>
                    <div className='span6'>
                        <h4>Model settings</h4>
                        <table className="table table-condensed table-striped">
                        </table>
                    </div>
                    <div className='span6'>
                        <h4>Optimization</h4>
                        <table className="table table-condensed table-striped">
                        </table>
                    </div>
                </div>
                <div className='row-fluid'>
                    <h4>Parameter assignment</h4>
                    <table className="table table-condensed table-striped">
                    </table>
                </div>
            </div>
        );
    }

    renderEditMode(){
        return (
            <div className="modal-body">
                <form className="form-horizontal">
                    <div className='row-fluid'>
                        <fieldset className='span6'>
                            <legend>Model assignments</legend>
                            <div></div>
                        </fieldset>
                        <fieldset className='span6'>
                            <legend>Optimizer assignments</legend>
                            <div></div>
                        </fieldset>
                    </div>
                    <div className='row-fluid'>
                        <fieldset>
                            <legend>Parameter assignments</legend>
                            <div></div>
                        </fieldset>
                    </div>
                </form>
            </div>
        );
    }

    render() {
        let {editMode} = this.props,
            modelName = 'Multistage',
            title = (editMode)?`Edit ${modelName} options`: `${modelName} options`,
            tableFunc = (editMode)? this.renderEditMode: this.renderReadOnly;

        return (
            <div className="modal hide fade"  id={types.OPTION_MODAL_ID}>

                <div className="modal-header">
                    <button className="close" type="button" data-dismiss="modal">×</button>
                    <h3>{title}</h3>
                </div>

                {tableFunc()}

                <EditableModalFooter
                    editMode={editMode}
                    handleSave={this.props.handleSave}
                    handleDelete={this.props.handleDelete} />
            </div>
        );
    }
}

ModelOptionModal.propTypes = {
    editMode: React.PropTypes.bool.isRequired,
    handleSave: React.PropTypes.func.isRequired,
    handleDelete: React.PropTypes.func.isRequired,
};

export default ModelOptionModal;
