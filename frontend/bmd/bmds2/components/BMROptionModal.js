import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";
import h from "shared/utils/helpers";

import {BMR_MODAL_ID} from "../constants";
import BaseModal from "./BaseModal";
import EditableModalFooter from "./EditableModalFooter";

class BMROptionModal extends BaseModal {
    UNSAFE_componentWillReceiveProps(nextProps) {
        if (nextProps.bmr) {
            this.setState(h.deepCopy(nextProps.bmr));
        }
    }

    handleSave() {
        let bmr = this.state;
        bmr.value = parseFloat(bmr.value);
        bmr.confidence_level = parseFloat(bmr.confidence_level);
        this.props.handleSave(bmr);
    }

    handleTypeChange(e) {
        let d = h.deepCopy(this.props.allOptions[e.target.value]);
        this.setState(d);
    }

    handleChange(e) {
        let d = {};
        d[e.target.name] = e.target.value;
        this.setState(d);
    }

    renderReadOnlyTable() {
        let {bmr} = this.props;
        return (
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
        );
    }

    renderEditingForm() {
        let {allOptions} = this.props,
            state = this.state,
            opts = _.values(allOptions);

        return (
            <form className="container-fluid">
                <div className="form-group form-row">
                    <label htmlFor="bmr_type">BMR type</label>
                    <select
                        id="bmr_type"
                        name="type"
                        className="form-control"
                        value={state.type}
                        onChange={this.handleTypeChange.bind(this)}>
                        {opts.map((d, i) => {
                            return (
                                <option key={i} value={d.type}>
                                    {d.type}
                                </option>
                            );
                        })}
                    </select>
                </div>

                <div className="form-group form-row">
                    <label htmlFor="bmr_value">BMR value</label>
                    <input
                        id="bmr_value"
                        name="value"
                        type="number"
                        className="form-control"
                        step="any"
                        value={state.value}
                        onChange={this.handleChange.bind(this)}
                    />
                </div>

                <div className="form-group form-row">
                    <label htmlFor="bmr_confidence_level">BMR confidence level</label>
                    <input
                        id="bmr_confidence_level"
                        name="confidence_level"
                        type="number"
                        className="form-control"
                        step="any"
                        value={state.confidence_level}
                        onChange={this.handleChange.bind(this)}
                    />
                </div>
            </form>
        );
    }

    render() {
        if (!this.props.bmr) {
            return null;
        }

        let {editMode, bmr} = this.props,
            title = this.props.editMode
                ? `Edit benchmark response: ${bmr.type}`
                : `Benchmark response: ${bmr.type}`,
            tableFunc = editMode ? this.renderEditingForm : this.renderReadOnlyTable;

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

                        <div className="modal-body">{tableFunc.bind(this)()}</div>

                        <EditableModalFooter
                            editMode={editMode}
                            handleSave={this.handleSave.bind(this)}
                            handleDelete={this.props.handleDelete}
                        />
                    </div>
                </div>
            </div>
        );
    }
}

BMROptionModal.propTypes = {
    bmr: PropTypes.object,
    allOptions: PropTypes.object.isRequired,
    editMode: PropTypes.bool.isRequired,
    handleSave: PropTypes.func.isRequired,
    handleDelete: PropTypes.func.isRequired,
};

export default BMROptionModal;
