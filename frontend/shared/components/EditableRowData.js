import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

const moveArrayElementUp = h.moveArrayElementUp,
    moveArrayElementDown = h.moveArrayElementDown,
    deleteArrayElement = h.deleteArrayElement,
    ActionsTh = function(props) {
        return (
            <th>
                Actions
                {props.onClickNew ? (
                    <button
                        className="btn btn-sm btn-primary mx-2"
                        title="New row"
                        onClick={props.onClickNew}>
                        <i className="fa fa-fw fa-plus"></i>
                    </button>
                ) : null}
            </th>
        );
    },
    MoveRowTd = function(props) {
        return (
            <td>
                {props.onEdit ? (
                    <button
                        className="btn btn-sm btn-primary px-1 mr-1"
                        title="Edit row"
                        onClick={props.onEdit}>
                        <i className="fa fa-fw fa-pencil-square-o"></i>
                    </button>
                ) : null}
                {props.onMoveUp ? (
                    <button
                        className="btn btn-sm btn-secondary px-1"
                        title="Move row up"
                        onClick={props.onMoveUp}>
                        <i className="fa fa-fw fa-long-arrow-up"></i>
                    </button>
                ) : null}

                {props.onMoveDown ? (
                    <button
                        className="btn btn-sm btn-secondary px-1 mx-1"
                        title="Move row down"
                        onClick={props.onMoveDown}>
                        <i className="fa fa-fw fa-long-arrow-down"></i>
                    </button>
                ) : null}

                {props.onDelete ? (
                    <button
                        className="btn btn-sm btn-danger px-1"
                        title="Delete row"
                        onClick={props.onDelete}>
                        <i className="fa fa-fw fa-trash"></i>
                    </button>
                ) : null}
            </td>
        );
    };

class EditableRow extends Component {
    constructor(props) {
        super(props);
        this.state = {edit: props.initiallyEditable};
    }

    render() {
        if (this.state.edit) {
            return this.renderEditRow(this.props.row, this.props.index);
        }
        return this.renderViewRow(this.props.row, this.props.index);
    }

    renderViewRow(row, index) {
        throw new Error("Requires implementation");
    }

    renderEditRow(row, index) {
        throw new Error("Requires implementation");
    }
}
EditableRow.propTypes = {
    initiallyEditable: PropTypes.bool.isRequired,
    row: PropTypes.object.isRequired,
    index: PropTypes.number.isRequired,
};

ActionsTh.propTypes = {
    onClickNew: PropTypes.func,
};
MoveRowTd.propTypes = {
    onEdit: PropTypes.func,
    onMoveUp: PropTypes.func,
    onMoveDown: PropTypes.func,
    onDelete: PropTypes.func,
};

export {
    ActionsTh,
    deleteArrayElement,
    EditableRow,
    moveArrayElementDown,
    moveArrayElementUp,
    MoveRowTd,
};
