import React from 'react';

import * as types from 'bmd/constants';


class ModelOptionModal extends React.Component {

    render() {
        let modelName = 'Multistage';
        return (
            <div className="modal hide fade"  id={types.OPTION_MODAL_ID}>

                <div className="modal-header">
                    <button className="close" type="button" data-dismiss="modal">×</button>
                    <h3>{modelName} model options</h3>
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

                <div className="modal-footer">
                    <button type='button'
                        className='btn btn-primary'
                        data-dismiss='modal'>Close</button>
                </div>
            </div>
        );
    }
}

ModelOptionModal.propTypes = {
};

export default ModelOptionModal;
