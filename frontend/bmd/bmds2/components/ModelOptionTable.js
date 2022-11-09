import PropTypes from "prop-types";
import React from "react";
import {ActionItem, ActionsButton} from "shared/components/ActionsButton";

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

        const actionItems = [
            <ActionItem key={0} label="Add all models" onClick={this.props.handleAddAll} />,
            <ActionItem key={1} label="Remove all models" onClick={this.props.handleRemoveAll} />,
        ];
        if (showVariance) {
            actionItems.push(
                <ActionItem
                    key={2}
                    label="Toggle all variance models"
                    onClick={this.props.handleVarianceToggle}
                />
            );
        }

        return (
            <div className="form-row">
                <div className="col-md-3">
                    <label>Add new model</label>
                </div>
                <div className="col-md-6">
                    <div className="form-group input-group">
                        <select className="form-control" ref={this.modelSelector}>
                            {allOptions.map((d, i) => {
                                return (
                                    <option key={i} value={i}>
                                        {d.name}
                                    </option>
                                );
                            })}
                        </select>
                        <div className="input-group-append">
                            <button
                                onClick={() => {
                                    let modelName = $(this.modelSelector.current).val();
                                    this.props.handleCreateModel(modelName);
                                }}
                                type="button"
                                className="btn btn-light btn-sm px-3">
                                <i className="fa fa-plus" />
                            </button>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <ActionsButton dropdownClasses="btn-light" items={actionItems} />
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
