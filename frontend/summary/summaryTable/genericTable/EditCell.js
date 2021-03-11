import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import h from "shared/utils/helpers";

import Modal from "shared/components/Modal";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import IntegerInput from "shared/components/IntegerInput";

import {getCellExcelName} from "./common";

@observer
class QuickEditCell extends Component {
    render() {
        const {store} = this.props;
        return (
            <>
                <QuillTextInput
                    value={store.stagedCell.quill_text}
                    onChange={value => store.updateStagedValue("quill_text", value)}
                />
                <div className="float-right">
                    <button
                        className="btn btn-light px-3 mr-2"
                        onClick={() => store.closeEditModal(false)}>
                        <i className="fa fa-times"></i>
                    </button>
                    <button
                        className="btn btn-primary px-3"
                        onClick={() => store.closeEditModal(true)}>
                        <i className="fa fa-check"></i>
                    </button>
                </div>
            </>
        );
    }
}
QuickEditCell.propTypes = {
    store: PropTypes.object.isRequired,
};

@observer
class EditCellModal extends Component {
    render() {
        const {store} = this.props,
            {editCell, stagedCell} = store;
        return (
            <Modal isShown={store.showCellModal} onClosed={() => store.closeEditModal(false)}>
                {editCell ? (
                    <>
                        <div className="modal-header">
                            <h4>Cell {getCellExcelName(editCell)}</h4>
                            <button
                                type="button"
                                className="float-right close"
                                onClick={() => store.closeEditModal(false)}
                                aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div className="modal-body container-fluid">
                            <div className="row">
                                {store.showHeaderInput ? (
                                    <div className="col-md-4">
                                        <CheckboxInput
                                            name="header"
                                            label="Header"
                                            helpText="This cell is a part of a header row."
                                            checked={stagedCell.header}
                                            onChange={e =>
                                                store.updateStagedValue(
                                                    e.target.name,
                                                    e.target.checked
                                                )
                                            }
                                        />
                                    </div>
                                ) : null}

                                {store.getMaxRowSpanRange > 1 ? (
                                    <div className="col-md-4">
                                        <IntegerInput
                                            minimum={1}
                                            maximum={store.getMaxRowSpanRange}
                                            name="row_span"
                                            label="# of rows to merge"
                                            helpText="Row-span (merges rows). Changing to a value greater than 1 will delete existing cells and remove content from those cells."
                                            onChange={e =>
                                                store.updateStagedValue(
                                                    e.target.name,
                                                    parseInt(e.target.value)
                                                )
                                            }
                                            value={stagedCell.row_span}
                                            slider={true}
                                        />
                                    </div>
                                ) : null}

                                {store.getMaxColSpanRange > 1 ? (
                                    <div className="col-md-4">
                                        <IntegerInput
                                            minimum={1}
                                            maximum={store.getMaxColSpanRange}
                                            name="col_span"
                                            label="# of columns to merge"
                                            helpText="Column-span (merges columns). Changing to a value greater than 1 will delete existing cells and remove content from those cells."
                                            onChange={e =>
                                                store.updateStagedValue(
                                                    e.target.name,
                                                    parseInt(e.target.value)
                                                )
                                            }
                                            value={stagedCell.col_span}
                                            slider={true}
                                        />
                                    </div>
                                ) : null}
                            </div>
                            <div className="row">
                                <div className="col-md-12">
                                    <QuillTextInput
                                        name="caption"
                                        label="Cell content"
                                        value={stagedCell.quill_text}
                                        onChange={value =>
                                            store.updateStagedValue("quill_text", value)
                                        }
                                    />
                                </div>
                            </div>

                            {store.editCellErrorText ? (
                                <div className="alert alert-danger">{store.editCellErrorText}</div>
                            ) : null}
                        </div>
                        <div className="modal-footer">
                            <div className="mr-auto">
                                {store.editCell.row == 0 ? (
                                    <button
                                        type="button"
                                        className="btn btn-danger mr-1"
                                        onClick={() => store.deleteColumn(editCell.column)}>
                                        <i className="fa fa-trash mr-1"></i>
                                        Delete column {h.excelColumn(editCell.column)}
                                    </button>
                                ) : null}

                                {store.editCell.column == 0 ? (
                                    <button
                                        type="button"
                                        className="btn btn-danger mr-1"
                                        onClick={() => store.deleteRow(editCell.row)}>
                                        <i className="fa fa-trash mr-1"></i>
                                        Delete row #{editCell.row + 1}
                                    </button>
                                ) : null}
                            </div>

                            <div className="mr-auto">
                                {store.editCell.row == 0 && editCell.column != 0 ? (
                                    <button
                                        type="button"
                                        className="btn btn-warning mr-1"
                                        onClick={() =>
                                            store.swapColumns(editCell.column, editCell.column - 1)
                                        }>
                                        <i className="fa fa-arrow-left mr-1"></i>
                                        Left
                                    </button>
                                ) : null}

                                {store.editCell.row == 0 &&
                                editCell.column < store.totalColumns - 1 ? (
                                    <button
                                        type="button"
                                        className="btn btn-warning mr-1"
                                        onClick={() =>
                                            store.swapColumns(editCell.column, editCell.column + 1)
                                        }>
                                        <i className="fa fa-arrow-right mr-1"></i>
                                        Right
                                    </button>
                                ) : null}

                                {editCell.column == 0 && editCell.row != 0 ? (
                                    <button
                                        type="button"
                                        className="btn btn-warning mr-1"
                                        onClick={() =>
                                            store.swapRows(editCell.row, editCell.row - 1)
                                        }>
                                        <i className="fa fa-arrow-up mr-1"></i>
                                        Up
                                    </button>
                                ) : null}
                                {editCell.column == 0 && editCell.row < store.totalRows - 1 ? (
                                    <button
                                        type="button"
                                        className="btn btn-warning"
                                        onClick={() =>
                                            store.swapRows(editCell.row, editCell.row + 1)
                                        }>
                                        <i className="fa fa-arrow-down mr-1"></i>
                                        Down
                                    </button>
                                ) : null}
                            </div>

                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={() => store.closeEditModal(false)}>
                                Close
                            </button>

                            <button
                                type="button"
                                className="btn btn-primary"
                                onClick={() => store.closeEditModal(true)}>
                                <i className="fa fa-save mr-1"></i>
                                Save changes
                            </button>
                        </div>
                    </>
                ) : (
                    <div></div>
                )}
            </Modal>
        );
    }
}

EditCellModal.propTypes = {
    store: PropTypes.object.isRequired,
};

export {QuickEditCell, EditCellModal};
