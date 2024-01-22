import PropTypes from "prop-types";
import React from "react";

const moveArrayElementUp = function (arr, index) {
        if (index === 0) {
            return;
        }
        let b = arr[index];
        arr[index] = arr[index - 1];
        arr[index - 1] = b;
        return arr;
    },
    moveArrayElementDown = function (arr, index) {
        if (index + 1 >= arr.length) {
            return;
        }
        let b = arr[index];
        arr[index] = arr[index + 1];
        arr[index + 1] = b;
        return arr;
    },
    deleteArrayElement = function (arr, index) {
        arr.splice(index, 1);
        return arr;
    },
    ActionsTh = function (props) {
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
    MoveRowTd = function (props) {
        return (
            <td>
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

ActionsTh.propTypes = {
    onClickNew: PropTypes.func,
};
MoveRowTd.propTypes = {
    onMoveUp: PropTypes.func,
    onMoveDown: PropTypes.func,
    onDelete: PropTypes.func,
};

export {ActionsTh, deleteArrayElement, moveArrayElementDown, moveArrayElementUp, MoveRowTd};
