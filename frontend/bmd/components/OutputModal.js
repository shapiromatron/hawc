import $ from "$";
import React from "react";
import PropTypes from "prop-types";

import * as types from "bmd/constants";
import BaseModal from "./BaseModal";

class OutputModal extends BaseModal {
    componentDidUpdate() {
        $(this.modalBody).animate({scrollTop: 0}, "fast");
    }

    renderBody(model, i) {
        if (model.execution_error) {
            return (
                <div key={i} className="alert alert-danger">
                    <p>
                        An error occurred during BMDS execution, please report to HAWC
                        administrators if the error continues to occur.
                    </p>
                </div>
            );
        }

        return <pre key={i}>{model.outfile}</pre>;
    }

    render() {
        let {models} = this.props;

        if (models.length === 0) {
            return null;
        }

        return (
            <div className="modal hide fade" tabIndex="-1" id={types.OUTPUT_MODAL_ID} role="dialog">
                <div className="modal-header">
                    <button refs="closer" className="close" type="button" data-dismiss="modal">
                        ×
                    </button>
                    <h3>{models[0].name} model output</h3>
                </div>

                <div className="modal-body" ref={c => this.modalBody = c}>
                    {models.map(this.renderBody)}
                </div>

                <div className="modal-footer">
                    <button type="button" className="btn btn-primary" data-dismiss="modal">
                        Close
                    </button>
                </div>
            </div>
        );
    }
}

OutputModal.propTypes = {
    models: PropTypes.arrayOf(PropTypes.object),
};

export default OutputModal;
