import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Modal from "shared/components/Modal";
import QuillTextInput from "shared/components/QuillTextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import IntegerInput from "shared/components/IntegerInput";

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
                <button className="btn btn-primary px-3" onClick={() => store.closeEditModal(true)}>
                    <i className="fa fa-check"></i>
                </button>
                <button
                    className="btn btn-light px-3 ml-1"
                    onClick={() => store.closeEditModal(false)}>
                    <i className="fa fa-times"></i>
                </button>
            </>
        );
    }
}
QuickEditCell.propTypes = {
    store: PropTypes.object.isRequired,
};

@observer
class EditCell extends Component {
    render() {
        const {store} = this.props,
            {editCell, stagedCell} = store;
        return (
            <Modal isShown={store.showCellModal} onClosed={() => store.closeEditModal(false)}>
                {editCell ? (
                    <>
                        <div className="modal-header">
                            <h4>
                                Edit Cell[{editCell.row + 1}, {editCell.column + 1}]
                            </h4>
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
                                            label="Row span"
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
                                            label="Column span"
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
                        </div>
                        <div className="modal-footer">
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

EditCell.propTypes = {
    store: PropTypes.object.isRequired,
};

export {QuickEditCell, EditCell};
