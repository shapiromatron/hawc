import React from 'react';

import * as types from 'bmd/constants';


class OutputModal extends React.Component {

    render() {
        var modelName = 'Multistage';
        return (
            <div className="modal hide fade" tabindex="-1" id={types.OUTPUT_MODAL_ID} role="dialog">

                <div className="modal-header">
                    <button className="close" type="button" data-dismiss="modal">×</button>
                    <h3>{modelName} model output</h3>
                </div>

                <div className="modal-body">
                    <pre></pre>
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

OutputModal.propTypes = {
};

export default OutputModal;
