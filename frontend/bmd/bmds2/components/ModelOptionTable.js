import React from "react";
import PropTypes from "prop-types";

import ModelOptionOverrideList from "../containers/ModelOptionOverrideList";

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
            <div className="row">
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
                        className="btn btn-sm">
                        <i className="icon-plus" />
                    </button>

                    <div className="btn-group float-right">
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

    render() {
        const {editMode, models} = this.props;
        return (
            <div className="col-6">
                <h4>Model options</h4>
                <table className="table table-sm table-striped">
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
                                    <td>
                                        <ModelOptionOverrideList index={i} />
                                    </td>
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
