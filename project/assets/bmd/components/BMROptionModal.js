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

    renderReadOnlyTable(){
        return (
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
        );
    }

    renderEditingForm(){
        return (
            <form className="form-horizontal">
                <div className="control-group form-row">
                    <label className="control-label"
                           for="bmr_type">BMR type</label>
                    <div className="controls">
                        <select id="bmr_type">
                        </select>
                    </div>
                </div>

                <div className="control-group form-row">
                    <label className="control-label"
                           for="bmr_value">BMR value</label>
                    <div className="controls">
                        <input id="bmr_value"></input>
                    </div>
                </div>

                <div className="control-group form-row">
                    <label className="control-label"
                           for="bmr_confidence_level">BMR confidence level</label>
                    <div className="controls">
                        <input id="bmr_confidence_level"></input>
                    </div>
                </div>
            </form>
        );
    }

    render() {

        let editMode = this.props.editMode,
            title = (this.props.editMode)?'Edit benchmark response': 'Benchmark response',
            tableFunc = (editMode)? this.renderEditingForm: this.renderReadOnlyTable;

        return (
            <div className="modal hide fade" role="dialog" id={types.BMR_MODAL_ID}>

                <div className="modal-header">
                    <button className="close" type="button"
                        data-dismiss="modal">×</button>
                    <h3>{title}</h3>
                </div>

                <div className="modal-body">
                    {tableFunc()}
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
    editMode: React.PropTypes.bool.isRequired,
};

export default BMROptionModal;
