import React from 'react';

import * as types from 'bmd/constants';


class BMROptionModal extends React.Component {

    render() {

        return (
            <div className="modal hide fade" role="dialog" id={types.BMR_MODAL_ID}>

                <div className="modal-header">
                    <button className="close" type="button"
                        data-dismiss="modal">×</button>
                    <h3>Benchmark response</h3>
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

                <div className="modal-footer">
                    <button className='btn btn-primary'
                        data-dismiss="modal">Close</button>
                </div>
            </div>
        );
    }
}

BMROptionModal.propTypes = {
};

export default BMROptionModal;
