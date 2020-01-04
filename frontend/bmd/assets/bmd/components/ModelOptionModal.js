import _ from 'lodash';
import React from 'react';
import PropTypes from 'prop-types';

import * as types from 'bmd/constants';

import BaseModal from './BaseModal';
import EditableModalFooter from 'bmd/components/EditableModalFooter';
import ModelOptionField from 'bmd/components/ModelOptionField';
import ParameterField from 'bmd/components/ParameterField';

class ModelOptionModal extends BaseModal {
    _getDefaults(model) {
        let defaults = {};
        _.each(model.defaults, (v, k) => {
            let val = v.d;
            if (v.t === 'b') {
                val = val === 1;
            }
            defaults[v.key] = val;
        });
        return defaults;
    }

    componentWillReceiveProps(nextProps) {
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
                <div className="row-fluid">
                    <div className="span6">
                        <h4>Model settings</h4>
                        <table className="table table-condensed table-striped" />
                    </div>
                    <div className="span6">
                        <h4>Optimization</h4>
                        <table className="table table-condensed table-striped" />
                    </div>
                </div>
                <div className="row-fluid">
                    <h4>Parameter assignment</h4>
                    <table className="table table-condensed table-striped" />
                </div>
            </div>
        );
    }

    handleInputChange(d, e) {
        let update = {},
            name = e.target.name;

        switch (d.t) {
            case 'i':
            case 'dd':
            case 'rp':
                update[name] = parseInt(e.target.value) || 0;
                break;
            case 'd':
                update[name] = parseFloat(e.target.value) || 0;
                break;
            case 'b':
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
        let { model } = this.props,
            getOpts = function(type) {
                return _.chain(model.defaults)
                    .values()
                    .filter((d) => d.c === type && d.n !== undefined)
                    .value();
            },
            models = getOpts('ot'),
            optimizers = getOpts('op'),
            params = getOpts('p');

        return (
            <div className="modal-body">
                <form className="form-horizontal">
                    <div className="row-fluid">
                        <fieldset className="span6">
                            <legend>Model assignments</legend>
                            <div>
                                {models.map((d, i) => {
                                    return (
                                        <ModelOptionField
                                            index={i}
                                            settings={d}
                                            handleChange={this.handleInputChange.bind(this, d)}
                                            value={this.state[d.key]}
                                        />
                                    );
                                })}
                            </div>
                        </fieldset>
                        <fieldset className="span6">
                            <legend>Optimizer assignments</legend>
                            <div>
                                {optimizers.map((d, i) => {
                                    return (
                                        <ModelOptionField
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
                    <div className="row-fluid">
                        <fieldset>
                            <legend>Parameter assignments</legend>
                            <div>
                                {params.map((d, i) => {
                                    return (
                                        <ParameterField
                                            index={i}
                                            settings={d}
                                            handleChange={this.handleParameterChange.bind(this, d)}
                                            value={this.state[d.key]}
                                        />
                                    );
                                })}
                            </div>
                        </fieldset>
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
                if (v.t === 'b') {
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

        let { editMode, model } = this.props,
            title = editMode ? `Edit ${model.name} options` : `${model.name} options`,
            tableFunc = editMode ? this.renderEditMode : this.renderReadOnly;

        return (
            <div className="modal hide fade" id={types.OPTION_MODAL_ID}>
                <div className="modal-header">
                    <button ref="closer" className="close" type="button" data-dismiss="modal">
                        ×
                    </button>
                    <h3>{title}</h3>
                </div>

                {tableFunc.bind(this)()}

                <EditableModalFooter
                    editMode={editMode}
                    handleSave={this.handleSave.bind(this)}
                    handleDelete={this.props.handleDelete}
                />
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
