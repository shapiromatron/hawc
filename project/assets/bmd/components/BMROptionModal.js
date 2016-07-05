import React from 'react';

import * as types from 'bmd/constants';

import EditableModalFooter from 'bmd/components/EditableModalFooter';


class BMROptionModal extends React.Component {

    handleSave(){
        console.log('handled');
    }

    handleDelete(){
        console.log('handled');
    }

    render() {

        let editMode = this.props.editMode,
            titlePrefix = (this.props.editMode)?'Edit ': '';

        return (
            <div className="modal hide fade" role="dialog" id={types.BMR_MODAL_ID}>

                <div className="modal-header">
                    <button className="close" type="button"
                        data-dismiss="modal">×</button>
                    <h3>{titlePrefix} Benchmark response</h3>
                </div>

                <div className="modal-body">
                    <table className="table table-condensed table-striped">
                        <tbody>
                            <tr>
                                <th style={{width: '50%'}}>BMR type</th>
                                <td style={{width: '50%'}}></td>
                            </tr>
                            <tr>
                                <th>Value</th>
                                <td></td>
                            </tr>
                            <tr>
                                <th>Confidence level</th>
                                <td></td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <EditableModalFooter
                    editMode={editMode}
                    handleSave={this.handleSave.bind(this)}
                    handleDelete={this.handleDelete.bind(this)} />
            </div>
        );
    }
}

BMROptionModal.propTypes = {
    editMode: React.PropTypes.bool,
};

export default BMROptionModal;
