import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";

import EditableModalFooter from "../components/EditableModalFooter";
import ModelOptionField from "../components/ModelOptionField";
import ParameterField from "../components/ParameterField";
import * as types from "../constants";
import BaseModal from "./BaseModal";

class ModelOptionModal extends BaseModal {
    _getDefaults(model) {
        let defaults = {};
        _.each(model.defaults, (v, k) => {
            let val = v.d;
            if (v.t === "b") {
                val = val === 1;
            }
            defaults[v.key] = val;
        });
        return defaults;
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        if (nextProps.model) {
            var props = Object.assign(
                this._getDefaults(nextProps.model),
                nextProps.model.overrides
            );
            this.setState(props);
        }
    }

    renderReadOnly() {
        return (
            <div className="modal-body">
                <div className="row">
                    <div className="col-md-6">
                        <h4>Model settings</h4>
                        <table className="table table-sm table-striped" />
                    </div>
                    <div className="col-md-6">
                        <h4>Optimization</h4>
                        <table className="table table-sm table-striped" />
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-12">
                        <h4>Parameter assignment</h4>
                    </div>
                    <div className="col-md-12">
                        <table className="table table-sm table-striped" />
                    </div>
                </div>
            </div>
        );
    }

    handleInputChange(d, e) {
        let update = {},
            name = e.target.name;

        switch (d.t) {
            case "i":
            case "dd":
            case "rp":
                update[name] = parseInt(e.target.value) || 0;
                break;
            case "d":
                update[name] = parseFloat(e.target.value) || 0;
                break;
            case "b":
                update[name] = e.target.checked;
                break;
            default:
                alert(`Invalid type: ${d.t}`);
                return null;
        }
        this.setState(update);
    }

    handleParameterChange(d, v) {
        let update = {};
        update[d.key] = v;
        this.setState(update);
    }

    renderEditMode() {
        let {model} = this.props,
            getOpts = function(type) {
                return _.chain(model.defaults)
                    .values()
                    .filter(d => d.c === type && d.n !== undefined)
                    .value();
            },
            models = getOpts("ot"),
            optimizers = getOpts("op"),
            params = getOpts("p");

        return (
            <div className="modal-body">
                <form className="container-fluid">
                    <div className="row">
                        <fieldset className="col-md-6">
                            <legend>Model assignments</legend>
                            <div>
                                {models.map((d, i) => {
                                    return (
                                        <ModelOptionField
                                            key={i}
                                            index={i}
                                            settings={d}
                                            handleChange={this.handleInputChange.bind(this, d)}
                                            value={this.state[d.key]}
                                        />
                                    );
                                })}
                            </div>
                            <p className="text-muted">
                                When ‟Doses to drop” is 0, no doses are dropped. If doses dropped is
                                greater than zero, doses are dropped from the maximum dose in
                                reverse order (e.g., a value of 1 drops the highest dose). All
                                models must have the same ‟Doses to Drop” value in order for a dose
                                to actually be dropped; otherwise it is ignored.
                            </p>
                        </fieldset>
                        <fieldset className="col-md-6">
                            <legend>Optimizer assignments</legend>
                            <div>
                                {optimizers.map((d, i) => {
                                    return (
                                        <ModelOptionField
                                            key={i}
                                            index={i}
                                            settings={d}
                                            handleChange={this.handleInputChange.bind(this, d)}
                                            value={this.state[d.key]}
                                        />
                                    );
                                })}
                            </div>
                        </fieldset>
                    </div>
                    <div className="row">
                        <div className="container-fluid col-md-12">
                            <legend className="row">Parameter assignments</legend>
                            {params.map((d, i) => {
                                return (
                                    <ParameterField
                                        key={i}
                                        index={i}
                                        settings={d}
                                        handleChange={this.handleParameterChange.bind(this, d)}
                                        value={this.state[d.key]}
                                    />
                                );
                            })}
                        </div>
                    </div>
                </form>
            </div>
        );
    }

    handleSave() {
        let overrides = {},
            state = this.state,
            val;

        _.each(this.props.model.defaults, (v, k) => {
            val = state[k];
            if (val !== undefined) {
                if (v.t === "b") {
                    val = val ? 1 : 0;
                }
                if (val !== v.d) {
                    overrides[k] = val;
                }
            }
        });

        this.props.handleSave(overrides);
    }

    render() {
        if (!this.props.model) {
            return null;
        }

        let {editMode, model} = this.props,
            title = editMode ? `Edit ${model.name} options` : `${model.name} options`,
            tableFunc = editMode ? this.renderEditMode : this.renderReadOnly;

        return (
            <div className="modal" id={types.OPTION_MODAL_ID}>
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

                        {tableFunc.bind(this)()}

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

ModelOptionModal.propTypes = {
    model: PropTypes.object,
    editMode: PropTypes.bool.isRequired,
    handleSave: PropTypes.func.isRequired,
    handleDelete: PropTypes.func.isRequired,
};

export default ModelOptionModal;
