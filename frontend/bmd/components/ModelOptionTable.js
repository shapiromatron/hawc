import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";

import {param_cw} from "bmd/constants";

class ModelOptionTable extends React.Component {
    constructor(props) {
        super(props);
        this.modelSelector = React.createRef();
    }

    handleCreateModel(event) {
        let modelName = $(this.modelSelector.current).val();
        this.props.handleCreateModel(modelName);
    }

    handleRowClick(modelIndex) {
        this.props.handleModalDisplay(modelIndex);
    }

    renderOption(d, i) {
        return (
            <option key={i} value={i}>
                {d.name}
            </option>
        );
    }

    renderOptionEdits() {
        if (!this.props.editMode) return;

        let {allOptions} = this.props;

        return (
            <div className="row">
                <label className="control-label">Add new model</label>
                <div className="controls">
                    <select style={{marginBottom: 0, marginRight: "1em"}} ref={this.modelSelector}>
                        {allOptions.map(this.renderOption)}
                    </select>
                    <button
                        onClick={this.handleCreateModel.bind(this)}
                        type="button"
                        className="btn btn-sm">
                        <i className="fa fa-plus" />
                    </button>

                    <div className="dropdown btn-group float-right">
                        <a className="btn dropdown-toggle" data-toggle="dropdown">
                            Actions &nbsp;
                            <span className="caret" />
                        </a>
                        <div className="dropdown-menu dropdown-menu-right">
                            <a className="dropdown-item" href="#" onClick={this.props.handleAddAll}>
                                Add all models
                            </a>
                            <a
                                className="dropdown-item"
                                href="#"
                                onClick={this.props.handleRemoveAll}>
                                Remove all models
                            </a>
                            {this.renderToggleVarianceBtn()}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    renderToggleVarianceBtn() {
        if (this.props.dataType !== "C") {
            return null;
        }

        return (
            <li>
                <a
                    href="#"
                    onClick={this.props.handleVarianceToggle}
                    title="Change the variance model for all continuous models">
                    Toggle all variance models
                </a>
            </li>
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
                        .filter(function(d2) {
                            return d.defaults[d2[0]].n !== undefined;
                        })
                        .map(function(d2) {
                            return <li key={d2[0]}>{getText(d2[0], d2[1])}</li>;
                        })
                        .value()}
                </ul>
            );
        }
    }

    renderRow(d, i) {
        let header = this.props.editMode ? "View/edit" : "View";

        return (
            <tr key={i}>
                <td>{d.name}</td>
                <td>{this.renderOverrideList(d)}</td>
                <td>
                    <button
                        type="button"
                        className="btn btn-link"
                        onClick={this.handleRowClick.bind(this, i)}>
                        {header}
                    </button>
                </td>
            </tr>
        );
    }

    render() {
        let header = this.props.editMode ? "View/edit" : "View";
        return (
            <div className="col-md-6">
                <h4>Model options</h4>
                <table className="table table-sm table-striped">
                    <thead>
                        <tr>
                            <th style={{width: "25%"}}>Model name</th>
                            <th style={{width: "60%"}}>Non-default settings</th>
                            <th style={{width: "15%"}}>{header}</th>
                        </tr>
                    </thead>
                    <tbody>{this.props.models.map(this.renderRow.bind(this))}</tbody>
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
