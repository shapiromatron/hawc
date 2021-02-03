import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Modal from "shared/components/Modal";

@observer
class CellModal extends Component {
    render() {
        const {store} = this.props,
            {editCell} = store;

        if (!editCell) {
            return null;
        }

        return (
            <Modal isShown={store.showCellModal} onClosed={store.hideCellModal}>
                <div className="modal-header">
                    <h1>Headering</h1>
                </div>
                <div className="modal-body">
                    {store.editCell.row}
                    {store.editCell.column}
                    {store.editCell.quill_text}
                </div>
                <div className="modal-footer">
                    <h1>footering</h1>
                </div>
            </Modal>
        );
    }
}

CellModal.propTypes = {
    store: PropTypes.object.isRequired,
};

export default CellModal;
