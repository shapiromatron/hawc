import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";

import ModalFooter from "../components/ModalFooter";
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

    componentDidUpdate(prevProps) {
        if (prevProps.model !== this.props.model && this.props.model) {
            var props = Object.assign(
                this._getDefaults(this.props.model),
                this.props.model.overrides
            );
            this.setState(props);
        }
    }

    render() {
        if (!this.props.model) {
            return null;
        }

        let {model} = this.props,
            title = `${model.name} options`;

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
                        <ModalFooter />
                    </div>
                </div>
            </div>
        );
    }
}

ModelOptionModal.propTypes = {
    model: PropTypes.object,
};

export default ModelOptionModal;
