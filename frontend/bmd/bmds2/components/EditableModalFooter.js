import React from "react";
import PropTypes from "prop-types";

class EditableModalFooter extends React.Component {
    renderEdit() {
        return (
            <div className="modal-footer">
                <button
                    type="button"
                    onClick={this.props.handleDelete}
                    className="btn btn-danger"
                    data-dismiss="modal">
                    Delete
                </button>
                <button
                    type="button"
                    onClick={this.props.handleSave}
                    className="btn btn-primary"
                    data-dismiss="modal">
                    Save and close
                </button>
                <button type="button" className="btn btn-light" data-dismiss="modal">
                    Cancel
                </button>
            </div>
        );
    }

    renderReadOnly() {
        return (
            <div className="modal-footer">
                <button type="button" className="btn btn-primary" data-dismiss="modal">
                    Close
                </button>
            </div>
        );
    }

    render() {
        return this.props.editMode ? this.renderEdit() : this.renderReadOnly();
    }
}

EditableModalFooter.propTypes = {
    editMode: PropTypes.bool.isRequired,
    handleSave: PropTypes.func.isRequired,
    handleDelete: PropTypes.func.isRequired,
};

export default EditableModalFooter;
