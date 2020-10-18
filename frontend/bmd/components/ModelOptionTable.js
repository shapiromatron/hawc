import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";

import {param_cw} from "../constants";

class ModelOptionTable extends React.Component {
    constructor(props) {
        super(props);
        this.modelSelector = React.createRef();
    }

    renderOptionEdits() {
        if (!this.props.editMode) {
            return;
        }

        let {allOptions} = this.props,
            showVariance = this.props.dataType === "C";

        return (
            <div className="row-fluid">
                <label className="control-label">Add new model</label>
                <div className="controls">
                    <select style={{marginBottom: 0, marginRight: "1em"}} ref={this.modelSelector}>
                        {allOptions.map((d, i) => {
                            return (
                                <option key={i} value={i}>
                                    {d.name}
                                </option>
                            );
                        })}
                    </select>
                    <button
                        onClick={() => {
                            let modelName = $(this.modelSelector.current).val();
                            this.props.handleCreateModel(modelName);
                        }}
                        type="button"
                        className="btn btn-small">
                        <i className="icon-plus" />
                    </button>

                    <div className="btn-group pull-right">
                        <a className="btn dropdown-toggle" data-toggle="dropdown">
                            Actions &nbsp;
                            <span className="caret" />
                        </a>
                        <ul className="dropdown-menu">
                            <li>
                                <a
                                    href="#"
                                    onClick={event => {
                                        event.preventDefault();
                                        this.props.handleAddAll();
                                    }}>
                                    Add all models
                                </a>
                            </li>
                            <li>
                                <a
                                    href="#"
                                    onClick={event => {
                                        event.preventDefault();
                                        this.props.handleRemoveAll();
                                    }}>
                                    Remove all models
                                </a>
                            </li>
                            {showVariance ? (
                                <li>
                                    <a
                                        href="#"
                                        onClick={event => {
                                            event.preventDefault();
                                            this.props.handleVarianceToggle();
                                        }}
                                        title="Change the variance model for all continuous models">
                                        Toggle all variance models
                                    </a>
                                </li>
                            ) : null}
                        </ul>
                    </div>
                </div>
            </div>
        );
    }

    renderOverrideList(d) {
        var getText = function(k, v) {
            let def = d.defaults[k],
                tmp;
            switch (def.t) {
                case "i":
                case "d":
                case "dd":
                case "rp":
                    return (
                        <span>
                            <b>{def.n}:</b> {v}
                        </span>
                    );
                case "b":
                    tmp = v === 1 ? "fa fa-check-square-o" : "fa fa-square-o";
                    return (
                        <span>
                            <b>{def.n}:</b> <i className={tmp} />
                        </span>
                    );
                case "p":
                    v = v.split("|");
                    return (
                        <span>
                            <b>{def.n}:</b> {param_cw[v[0]]} to {v[1]}
                        </span>
                    );
                default:
                    alert(`Invalid type: ${d.t}`);
                    return null;
            }
        };

        if (_.isEmpty(d.overrides)) {
            return <span>-</span>;
        } else {
            return (
                <ul>
                    {_.chain(d.overrides)
                        .toPairs()
                        .filter(d2 => d.defaults[d2[0]].n !== undefined)
                        .map(d2 => <li key={d2[0]}>{getText(d2[0], d2[1])}</li>)
                        .value()}
                </ul>
            );
        }
    }

    render() {
        const {editMode, models} = this.props;
        return (
            <div className="span6">
                <h4>Model options</h4>
                <table className="table table-condensed table-striped">
                    <thead>
                        <tr>
                            <th style={{width: "25%"}}>Model name</th>
                            <th style={{width: "60%"}}>Non-default settings</th>
                            <th style={{width: "15%"}}>{editMode ? "View/edit" : "View"}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {models.map((d, i) => {
                            return (
                                <tr key={i}>
                                    <td>{d.name}</td>
                                    <td>{this.renderOverrideList(d)}</td>
                                    <td>
                                        <button
                                            type="button"
                                            className="btn btn-link"
                                            onClick={() => this.props.handleModalDisplay(i)}>
                                            {editMode ? "View/edit" : "View"}
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
                {this.renderOptionEdits()}
            </div>
        );
    }
}

ModelOptionTable.propTypes = {
    editMode: PropTypes.bool.isRequired,
    dataType: PropTypes.string.isRequired,
    handleVarianceToggle: PropTypes.func.isRequired,
    handleAddAll: PropTypes.func.isRequired,
    handleRemoveAll: PropTypes.func.isRequired,
    handleCreateModel: PropTypes.func.isRequired,
    handleModalDisplay: PropTypes.func.isRequired,
    models: PropTypes.array.isRequired,
    allOptions: PropTypes.array.isRequired,
};

export default ModelOptionTable;
