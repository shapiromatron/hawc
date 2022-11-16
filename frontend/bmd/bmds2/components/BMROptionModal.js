import PropTypes from "prop-types";
import React from "react";

import h from "/shared/utils/helpers";

import {BMR_MODAL_ID} from "../constants";
import BaseModal from "./BaseModal";
import ModalFooter from "./ModalFooter";

class BMROptionModal extends BaseModal {
    UNSAFE_componentWillReceiveProps(nextProps) {
        if (nextProps.bmr) {
            this.setState(h.deepCopy(nextProps.bmr));
        }
    }

    render() {
        if (!this.props.bmr) {
            return null;
        }

        let {bmr} = this.props,
            title = `Benchmark response: ${bmr.type}`;

        return (
            <div className="modal" id={BMR_MODAL_ID}>
                <div className="modal-dialog">
                    <div className="modal-content">
                        <div className="modal-header">
                            <h3>{title}</h3>
                            <button
                                ref={this.closer}
                                className="close"
                                type="button"
                                data-dismiss="modal">
                                ×
                            </button>
                        </div>
                        <div className="modal-body">
                            <table className="table table-sm table-striped">
                                <tbody>
                                    <tr>
                                        <th style={{width: "30%"}}>BMR type</th>
                                        <td style={{width: "70%"}}>{bmr.type}</td>
                                    </tr>
                                    <tr>
                                        <th>Value</th>
                                        <td>{bmr.value}</td>
                                    </tr>
                                    <tr>
                                        <th>Confidence level</th>
                                        <td>{bmr.confidence_level}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <ModalFooter />
                    </div>
                </div>
            </div>
        );
    }
}

BMROptionModal.propTypes = {
    bmr: PropTypes.object,
    allOptions: PropTypes.object.isRequired,
};

export default BMROptionModal;
