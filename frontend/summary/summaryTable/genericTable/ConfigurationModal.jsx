import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import Modal from "shared/components/Modal";

@observer
class ConfigurationModal extends Component {
    render() {
        const {store} = this.props,
            {settings} = store;
        return (
            <Modal
                isShown={store.showConfigurationModal}
                onClosed={() => store.setConfigurationModal(false)}>
                <div className="modal-header">
                    <h4>Table Configuration</h4>
                    <button
                        type="button"
                        className="float-right close"
                        onClick={() => store.setConfigurationModal(false)}
                        aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div className="modal-body container-fluid">
                    <div className="row">
                        <div className="col-md-12">
                            <CheckboxInput
                                name="interactive"
                                label="Table Interactivity"
                                helpText="If checked, enables sorting, filtering, and pagination of the table. The table should not have any merged cells to work as expected."
                                checked={settings.interactive}
                                onChange={e =>
                                    store.setConfiguration(e.target.name, e.target.checked)
                                }
                            />
                        </div>
                    </div>
                </div>
                <div className="modal-footer">
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => store.setConfigurationModal(false)}>
                        Close
                    </button>
                </div>
            </Modal>
        );
    }
}

ConfigurationModal.propTypes = {
    store: PropTypes.object.isRequired,
};

export default ConfigurationModal;
