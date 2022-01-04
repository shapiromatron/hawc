import _ from "lodash";
import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Alert from "shared/components/Alert";
import Loading from "shared/components/Loading";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import CheckboxInput from "shared/components/CheckboxInput";
import QuillTextInput from "shared/components/QuillTextInput";

import {robAttributeChoices} from "./constants";

class EditButton extends Component {
    render() {
        const {handleClick} = this.props;
        return (
            <button
                className="btn btn-light btn-sm float-right-absolute"
                key={0}
                onClick={handleClick}>
                <i className="fa fa-edit mr-1"></i>Edit
            </button>
        );
    }
}
EditButton.propTypes = {
    handleClick: PropTypes.func.isRequired,
};

@observer
class EditCellForm extends Component {
    render() {
        const {rowIdx, colIdx, store} = this.props,
            col = store.stagedEdits.columns[colIdx],
            row = store.stagedEdits.rows[rowIdx],
            customized = _.find(row.customized, d => d.key == col.key);
        return (
            <>
                <CheckboxInput
                    label="Customize?"
                    name="customize"
                    onChange={e =>
                        store.updateStagedCell(
                            rowIdx,
                            col.key,
                            e.target.checked ? store.getDefaultCustomized(row, col) : null
                        )
                    }
                    checked={customized != null}
                    helpText={"Overrides cell dimensions for calculated best fit"}
                />
                {customized != null
                    ? col.attribute == "rob_score"
                        ? this.renderRobForm()
                        : this.renderTextForm()
                    : null}
            </>
        );
    }
    renderRobForm() {
        const {rowIdx, colIdx, store} = this.props,
            col = store.stagedEdits.columns[colIdx],
            row = store.stagedEdits.rows[rowIdx],
            customized = _.find(row.customized, d => d.key == col.key),
            choices = store.scoreIdChoices(row.id, col.metric_id);
        return choices.length ? (
            <SelectInput
                choices={choices}
                value={customized.score_id}
                handleSelect={value =>
                    store.updateStagedCell(rowIdx, col.key, {key: col.key, score_id: value})
                }
                label="Score ID"
            />
        ) : (
            "No scores available"
        );
    }
    renderTextForm() {
        const {rowIdx, colIdx, store} = this.props,
            col = store.stagedEdits.columns[colIdx],
            customized = _.find(store.stagedEdits.rows[rowIdx].customized, d => d.key == col.key);
        return (
            <QuillTextInput
                label="Custom text"
                value={customized.html}
                onChange={value =>
                    store.updateStagedCell(rowIdx, col.key, {key: col.key, html: value})
                }
            />
        );
    }
}
EditCellForm.propTypes = {
    store: PropTypes.object.isRequired,
    rowIdx: PropTypes.number.isRequired,
    colIdx: PropTypes.number.isRequired,
};

@observer
class EditRowForm extends Component {
    render() {
        const {store, rowIdx} = this.props,
            row = store.stagedEdits.rows[rowIdx],
            typeChoices = store.rowTypeChoices,
            idChoices = store.rowIdChoices;
        return (
            <>
                <div className="col-md-12">
                    <SelectInput
                        choices={typeChoices}
                        value={row.type}
                        handleSelect={value => store.updateStagedRow(rowIdx, {type: value})}
                        label="Data type"
                    />
                </div>
                <div className="col-md-12">
                    <SelectInput
                        choices={idChoices}
                        value={row.id}
                        handleSelect={value => store.updateStagedRow(rowIdx, {id: parseInt(value)})}
                        label="Item"
                    />
                </div>
                <div className="col-md-12 text-center">
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={() => store.commitStagedEdits()}>
                            Update
                        </button>
                        <button
                            className="btn btn-sm btn-light"
                            onClick={() => store.resetStagedEdits()}>
                            Cancel
                        </button>
                    </div>
                    <div className="btn-group mx-2">
                        <button
                            className="btn btn-sm btn-light"
                            onClick={() => store.moveRow(rowIdx, -1)}>
                            <i className="fa fa-arrow-up"></i>
                        </button>
                        <button
                            className="btn btn-sm btn-light"
                            onClick={() => store.moveRow(rowIdx, 1)}>
                            <i className="fa fa-arrow-down"></i>
                        </button>
                    </div>
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-danger"
                            onClick={() => store.deleteRow(rowIdx)}>
                            Delete
                        </button>
                    </div>
                </div>
            </>
        );
    }
}
EditRowForm.propTypes = {
    store: PropTypes.object.isRequired,
    rowIdx: PropTypes.number.isRequired,
};

@observer
class EditColumnForm extends Component {
    render() {
        const {store, colIdx} = this.props,
            col = store.stagedEdits.columns[colIdx];
        return (
            <>
                <div className="col-md-12">
                    <TextInput
                        onChange={e => store.updateStagedColumn(colIdx, {label: e.target.value})}
                        name="label"
                        value={col.label}
                        label="Label"
                    />
                </div>
                <div className="col-md-12">
                    <SelectInput
                        choices={robAttributeChoices}
                        handleSelect={value => store.updateStagedColumn(colIdx, {attribute: value})}
                        value={col.attribute}
                        label="Attribute"
                    />
                    {col.attribute == "rob_score" ? (
                        <SelectInput
                            choices={store.metricIdChoices}
                            handleSelect={value =>
                                store.updateStagedColumn(colIdx, {metric_id: value})
                            }
                            value={col.metric_id}
                            label="Metric"
                        />
                    ) : null}
                </div>
                <div className="col-md-12 text-center">
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={() => store.commitStagedEdits()}>
                            Update
                        </button>
                        <button
                            className="btn btn-sm btn-light"
                            onClick={() => store.resetStagedEdits()}>
                            Cancel
                        </button>
                    </div>
                    <div className="btn-group mx-2">
                        <button
                            className="btn btn-sm btn-light"
                            onClick={() => store.moveColumn(colIdx, -1)}>
                            <i className="fa fa-arrow-left"></i>
                        </button>
                        <button
                            className="btn btn-sm btn-light"
                            onClick={() => store.moveColumn(colIdx, 1)}>
                            <i className="fa fa-arrow-right"></i>
                        </button>
                    </div>
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-danger"
                            onClick={() => store.deleteColumn(colIdx)}>
                            Delete
                        </button>
                    </div>
                </div>
            </>
        );
    }
}
EditColumnForm.propTypes = {
    store: PropTypes.object.isRequired,
    colIdx: PropTypes.number.isRequired,
};

@observer
class Table extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchData();
    }
    cellContents() {
        return 1;
    }
    render() {
        const {store, forceReadOnly} = this.props,
            editable = store.editMode && !forceReadOnly;
        if (store.isFetchingData) {
            return <Loading />;
        }
        if (!store.hasData) {
            return (
                <Alert message="No data are available. Studies must be published and have at least one endpoint to be available for this summary table." />
            );
        }

        const {numColumns, workingSettings, editColumnIndex, editRowIndex} = store;
        return (
            <table className="summaryTable table table-bordered table-sm">
                <thead>
                    <tr>
                        {workingSettings.columns.map((col, idx) => {
                            return (
                                <th key={col.key} className="position-relative">
                                    {editable && editColumnIndex === idx ? (
                                        <EditColumnForm store={store} colIdx={idx} />
                                    ) : (
                                        <>
                                            {editable && editRowIndex == null ? (
                                                <EditButton
                                                    handleClick={() =>
                                                        store.setEditColumnIndex(idx)
                                                    }
                                                />
                                            ) : null}
                                            {col.label}
                                        </>
                                    )}
                                </th>
                            );
                        })}
                    </tr>
                </thead>
                <tbody>
                    {workingSettings.rows.map((row, rowIdx) => {
                        return (
                            <tr key={rowIdx}>
                                {_.range(0, numColumns).map(colIdx => {
                                    return (
                                        <td key={colIdx} className="position-relative">
                                            {editable &&
                                            (rowIdx === editRowIndex ||
                                                colIdx === editColumnIndex) ? (
                                                <>
                                                    {rowIdx === editRowIndex && colIdx == 0 ? (
                                                        <EditRowForm
                                                            key={colIdx}
                                                            store={store}
                                                            rowIdx={rowIdx}
                                                        />
                                                    ) : null}
                                                    <EditCellForm
                                                        store={store}
                                                        rowIdx={rowIdx}
                                                        colIdx={colIdx}
                                                    />
                                                </>
                                            ) : (
                                                <>
                                                    {editable &&
                                                    editColumnIndex == null &&
                                                    colIdx === 0 ? (
                                                        <EditButton
                                                            handleClick={() =>
                                                                store.setEditRowIndex(rowIdx)
                                                            }
                                                        />
                                                    ) : null}
                                                    <span
                                                        dangerouslySetInnerHTML={{
                                                            __html: store.getCellContent(
                                                                rowIdx,
                                                                colIdx
                                                            ),
                                                        }}
                                                    />
                                                </>
                                            )}
                                        </td>
                                    );
                                })}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    }
}
Table.defaultProps = {
    forceReadOnly: false,
};
Table.propTypes = {
    store: PropTypes.object.isRequired,
    forceReadOnly: PropTypes.bool,
};

export default Table;
