import React from "react";

class ModalFooter extends React.Component {
    render() {
        return (
            <div className="modal-footer">
                <button type="button" className="btn btn-primary" data-dismiss="modal">
                    Close
                </button>
            </div>
        );
    }
}

ModalFooter.propTypes = {};

export default ModalFooter;
