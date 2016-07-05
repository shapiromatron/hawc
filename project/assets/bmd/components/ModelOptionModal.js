import React from 'react';

import * as types from 'bmd/constants';

import EditableModalFooter from 'bmd/components/EditableModalFooter';


class ModelOptionModal extends React.Component {

    handleSave(){
        console.log('handled');
    }

    handleDelete(){
        console.log('handled');
    }

    render() {
        let {editMode} = this.props,
            modelName = 'Multistage',
            titlePrefix = (editMode)?'Edit ': '';
        return (
            <div className="modal hide fade"  id={types.OPTION_MODAL_ID}>

                <div className="modal-header">
                    <button className="close" type="button" data-dismiss="modal">×</button>
                    <h3>{titlePrefix}{modelName} model options</h3>
                </div>

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

                <EditableModalFooter
                    editMode={editMode}
                    handleSave={this.handleSave.bind(this)}
                    handleDelete={this.handleDelete.bind(this)} />
            </div>
        );
    }
}

ModelOptionModal.propTypes = {
    editMode: React.PropTypes.bool,
};

export default ModelOptionModal;
