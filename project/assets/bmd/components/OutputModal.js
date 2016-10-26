import $ from '$';
import React from 'react';

import * as types from 'bmd/constants';


class OutputModal extends React.Component {

    componentDidUpdate(){
        $(this.refs.modalBody).animate({scrollTop: 0}, 'fast');
    }

    renderBody(){
        var { model } = this.props;

        if (model.execution_error){
            return <div className='alert alert-danger'>
                <p>
                An error occurred during BMDS execution, please report
                to HAWC administrators if the error continues to occur.
                </p>
            </div>;
        }

        return <pre>{model.outfile}</pre>;
    }

    render() {
        var { model } = this.props;

        if (!model){
            return null;
        }

        return (
            <div className="modal hide fade" tabIndex="-1" id={types.OUTPUT_MODAL_ID} role="dialog">

                <div className="modal-header">
                    <button className="close" type="button" data-dismiss="modal">×</button>
                    <h3>{model.name} model output</h3>
                </div>

                <div className="modal-body" ref='modalBody'>
                    {this.renderBody()}
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
    model: React.PropTypes.object,
};

export default OutputModal;
