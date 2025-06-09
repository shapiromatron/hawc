import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import Alert from "shared/components/Alert";
import CheckboxInput from "shared/components/CheckboxInput";
import IntegerInput from "shared/components/IntegerInput";
import Loading from "shared/components/Loading";
import QuillTextInput from "shared/components/QuillTextInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import {COL_ATTRIBUTE, ROW_TYPE, colAttributeChoices} from "./constants";

class EditButton extends Component {
    render() {
        const {handleClick} = this.props;
        return (
            <button className="btn btn-light btn-sm float-right" onClick={handleClick}>
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
                    label="Customize cell?"
                    onChange={e =>
                        store.updateStagedCell(
                            rowIdx,
                            col.key,
                            e.target.checked ? store.getDefaultCustomized(row, col) : null
                        )
                    }
                    checked={customized != null}
                />
                {customized != null
                    ? col.attribute == COL_ATTRIBUTE.ROB.id
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
            data = store.getDataSelection(row.type, row.id),
            customized = _.find(row.customized, d => d.key == col.key),
            choices = store.scoreIdChoices(data["study_id"], col.metric_id);
        return (
            <SelectInput
                choices={choices}
                value={customized.score_id}
                handleSelect={value =>
                    store.updateStagedCell(rowIdx, col.key, {
                        key: col.key,
                        score_id: parseInt(value),
                    })
                }
                label="Score"
            />
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
            rowTypeChoices = store.rowTypeChoices(row);
        return (
            <>
                <div className="col-md-12">
                    <SelectInput
                        choices={rowTypeChoices}
                        value={row.type}
                        handleSelect={value => {
                            let oldPriority = _.findIndex(rowTypeChoices, c => c.id == row.type),
                                newPriority = _.findIndex(rowTypeChoices, c => c.id == value),
                                id =
                                    oldPriority > newPriority
                                        ? store.getDataSelection(row.type, row.id)[`${value}_id`]
                                        : _.find(
                                              store.dataset.data,
                                              d =>
                                                  d["type"] == value &&
                                                  d[`${row.type}_id`] == row.id
                                          )["id"];
                            return store.updateStagedRow(rowIdx, {type: value, id: parseInt(id)});
                        }}
                        label="Data type"
                    />
                </div>
                <div className="col-md-12">{this.renderIdForm()}</div>
                <div className="col-md-12 text-center mb-3">
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={store.commitStagedEdits}>
                            Update
                        </button>
                        <button className="btn btn-sm btn-light" onClick={store.resetStagedEdits}>
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

    renderIdInput(type) {
        const {store, rowIdx} = this.props,
            row = store.stagedEdits.rows[rowIdx],
            data = store.getDataSelection(row.type, row.id),
            typeField = `${type.id}_id`;
        return (
            <SelectInput
                key={`${type.id}_input`}
                choices={store.rowIdChoices(row, type.id)}
                value={data[typeField]}
                handleSelect={value => {
                    let target = _.find(
                        store.dataset.data,
                        d => d["type"] == data["type"] && d[typeField] == parseInt(value)
                    );
                    store.updateStagedRow(rowIdx, {id: parseInt(target["id"])});
                }}
                label={type.label}
            />
        );
    }

    renderIdForm() {
        let inputs = [];
        const {store, rowIdx} = this.props,
            row = store.stagedEdits.rows[rowIdx];
        switch (row.type) {
            case ROW_TYPE.ANIMAL_GROUP.id:
                inputs.unshift(this.renderIdInput(ROW_TYPE.ANIMAL_GROUP));
            // falls through
            case ROW_TYPE.EXPERIMENT.id:
                inputs.unshift(this.renderIdInput(ROW_TYPE.EXPERIMENT));
            // falls through
            case ROW_TYPE.STUDY.id:
                inputs.unshift(this.renderIdInput(ROW_TYPE.STUDY));
        }
        return inputs;
    }
}
EditRowForm.propTypes = {
    store: PropTypes.object.isRequired,
    rowIdx: PropTypes.number.isRequired,
};

@observer
class EditSubheaderForm extends Component {
    render() {
        const {store, shIdx} = this.props,
            subheader = store.stagedEdits.subheaders[shIdx],
            {max, min} = store.getSubheaderBounds(shIdx);
        return (
            <>
                <div className="col-md-12">
                    <TextInput
                        onChange={e => store.updateStagedSubheader(shIdx, {label: e.target.value})}
                        name="label"
                        value={subheader.label}
                        label="Label"
                    />
                </div>
                <div className="col-md-12">
                    <IntegerInput
                        onChange={e => {
                            let value = parseInt(e.target.value),
                                start =
                                    value >= min && value <= max
                                        ? value
                                        : store.settings.subheaders[shIdx].start;
                            store.updateStagedSubheader(shIdx, {start});
                        }}
                        value={subheader.start}
                        name="start"
                        label="Start"
                    />
                </div>
                <div className="col-md-12">
                    <IntegerInput
                        onChange={e => {
                            let value = parseInt(e.target.value),
                                length =
                                    value >= 1 && value <= max - min + 1
                                        ? value
                                        : store.settings.subheaders[shIdx].length;
                            store.updateStagedSubheader(shIdx, {length});
                        }}
                        value={subheader.length}
                        name="length"
                        label="Length"
                    />
                </div>
                <div className="col-md-12 text-center">
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={store.commitStagedEdits}>
                            Update
                        </button>
                        <button className="btn btn-sm btn-light" onClick={store.resetStagedEdits}>
                            Cancel
                        </button>
                    </div>
                    <div className="btn-group ml-2">
                        <button
                            className="btn btn-sm btn-danger"
                            onClick={() => store.deleteSubheader(shIdx)}>
                            Delete
                        </button>
                    </div>
                </div>
            </>
        );
    }
}
EditSubheaderForm.propTypes = {
    store: PropTypes.object.isRequired,
    shIdx: PropTypes.number.isRequired,
};

@observer
class EditColumnForm extends Component {
    render() {
        const {store, colIdx} = this.props,
            col = store.stagedEdits.columns[colIdx];
        return (
            <>
                <div className="col-md-12">
                    <SelectInput
                        choices={colAttributeChoices[store.settings.data_source]}
                        handleSelect={value => store.updateStagedColumn(colIdx, {attribute: value})}
                        value={col.attribute}
                        label="Attribute"
                    />
                </div>
                {col.attribute == COL_ATTRIBUTE.ROB.id ? (
                    <div className="col-md-12">
                        <SelectInput
                            choices={store.metricIdChoices}
                            handleSelect={value =>
                                store.updateStagedColumn(colIdx, {metric_id: parseInt(value)})
                            }
                            value={col.metric_id}
                            label="Metric"
                        />
                    </div>
                ) : col.attribute == COL_ATTRIBUTE.ANIMAL_GROUP_DOSES.id ? (
                    <div className="col-md-12">
                        <SelectInput
                            choices={store.doseUnitChoices}
                            handleSelect={value =>
                                store.updateStagedColumn(colIdx, {dose_unit: value})
                            }
                            value={col.dose_unit}
                            label="Dose Units"
                        />
                    </div>
                ) : null}
                <div className="col-md-12">
                    <TextInput
                        onChange={e => store.updateStagedColumn(colIdx, {label: e.target.value})}
                        name="label"
                        value={col.label}
                        label="Label"
                    />
                </div>
                <div className="col-md-12">
                    <IntegerInput
                        minimum={1}
                        maximum={20}
                        onChange={e => {
                            let value = parseInt(e.target.value),
                                width =
                                    value >= 1 && value <= 20
                                        ? value
                                        : store.settings.columns[colIdx].width;
                            store.updateStagedColumn(colIdx, {width});
                        }}
                        value={col.width}
                        name="width"
                        label="Width"
                        helpPopup="Number between 1 and 20"
                    />
                </div>
                <div className="col-md-12 text-center">
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={store.commitStagedEdits}>
                            Update
                        </button>
                        <button className="btn btn-sm btn-light" onClick={store.resetStagedEdits}>
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
    getInteractiveIcon(rowIdx, colIdx) {
        const {store} = this.props,
            onClick = store.interactiveOnClick(rowIdx, colIdx);

        return onClick == null ? null : (
            <span className="previewModalIcon float-right">
                <i className="fa fa-external-link" onClick={onClick}></i>
            </span>
        );
    }
    renderSubheaders() {
        const {store, forceReadOnly} = this.props,
            editable = store.editMode && !forceReadOnly;

        const {workingSettings, editing, editingSubheader, editIndex} = store;

        let last = workingSettings.subheaders[workingSettings.subheaders.length - 1],
            length = last.start + last.length - 1;
        let subheaders = [],
            count = 0;
        for (let i = 0; i < length; i++) {
            let idx = count,
                subheader = workingSettings.subheaders[idx],
                item = null;
            if (subheader.start == i + 1) {
                item = (
                    <th
                        key={i}
                        className={
                            editable && editingSubheader && editIndex == idx ? "bg-light" : null
                        }
                        style={
                            editable && editingSubheader && editIndex == idx ? {minWidth: 300} : {}
                        }
                        colSpan={subheader.length}>
                        {editable && editingSubheader && editIndex == idx ? (
                            <EditSubheaderForm store={store} shIdx={idx} />
                        ) : (
                            <>
                                {editable && (editingSubheader || !editing) ? (
                                    <EditButton
                                        handleClick={() => store.setEditSubheaderIndex(idx)}
                                    />
                                ) : null}
                                {subheader.label}
                            </>
                        )}
                    </th>
                );
                i += subheader.length - 1;
                count++;
            } else {
                item = <th key={i}></th>;
            }
            subheaders.push(item);
        }
        return subheaders;
    }
    render() {
        const {store, forceReadOnly} = this.props,
            editable = store.editMode && !forceReadOnly;
        if (store.isFetching) {
            return <Loading />;
        }
        if (store.datasetError) {
            return <Alert message={store.datasetError} />;
        }
        if (!store.hasData) {
            return <Alert message="No data are available." />;
        }

        const {numColumns, workingSettings, editing, editingColumn, editingRow, editIndex} = store;

        return (
            <table className="summaryTable table table-bordered table-sm">
                <colgroup>
                    {_.map(store.columnWidths, (w, i) => {
                        return <col key={i} style={{width: `${w}%`}} />;
                    })}
                </colgroup>
                <thead>
                    {workingSettings.subheaders.length ? <tr>{this.renderSubheaders()}</tr> : null}
                    <tr>
                        {workingSettings.columns.map((col, idx) => {
                            return (
                                <th
                                    key={col.key}
                                    className={
                                        editable && editingColumn && editIndex == idx
                                            ? "bg-lightblue"
                                            : null
                                    }
                                    style={
                                        editable && editingColumn && editIndex == idx
                                            ? {minWidth: 300}
                                            : {}
                                    }>
                                    {editable && editingColumn && editIndex == idx ? (
                                        <EditColumnForm store={store} colIdx={idx} />
                                    ) : (
                                        <>
                                            {editable && (editingColumn || !editing) ? (
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
                        return store.getDataSelection(row.type, row.id) ? (
                            <tr
                                key={rowIdx}
                                className={
                                    editable && editingRow && editIndex == rowIdx
                                        ? "bg-lightblue"
                                        : null
                                }>
                                {workingSettings.columns.map((col, colIdx) => {
                                    let content = store.getCellContent(rowIdx, colIdx);
                                    return (
                                        <td
                                            key={colIdx}
                                            className={`previewModalParent${
                                                editable && store.editingCell(rowIdx, colIdx)
                                                    ? " bg-lightblue"
                                                    : col.attribute == COL_ATTRIBUTE.ROB.id
                                                      ? " text-center align-middle cursor-pointer"
                                                      : ""
                                            }`}
                                            style={
                                                editable && store.editingCell(rowIdx, colIdx)
                                                    ? {minWidth: 300}
                                                    : {backgroundColor: content.backgroundColor}
                                            }
                                            onClick={
                                                (editable && store.editingCell(rowIdx, colIdx)) ||
                                                col.attribute != COL_ATTRIBUTE.ROB.id
                                                    ? null
                                                    : store.interactiveOnClick(rowIdx, colIdx)
                                            }>
                                            {editable && store.editingCell(rowIdx, colIdx) ? (
                                                <>
                                                    {editingRow && colIdx == 0 ? (
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
                                                    <hr />
                                                </>
                                            ) : editable &&
                                              (editingRow || !editing) &&
                                              colIdx == 0 ? (
                                                <EditButton
                                                    handleClick={e => {
                                                        e.stopPropagation();
                                                        store.setEditRowIndex(rowIdx);
                                                    }}
                                                />
                                            ) : null}
                                            {(editable && store.editingCell(rowIdx, colIdx)) ||
                                            col.attribute == COL_ATTRIBUTE.ROB.id
                                                ? null
                                                : this.getInteractiveIcon(rowIdx, colIdx)}
                                            <span
                                                style={
                                                    editable && store.editingCell(rowIdx, colIdx)
                                                        ? {}
                                                        : {color: content.color}
                                                }
                                                dangerouslySetInnerHTML={{
                                                    __html: content.html,
                                                }}
                                            />
                                        </td>
                                    );
                                })}
                            </tr>
                        ) : (
                            <tr key={rowIdx}>
                                <td colSpan={numColumns}>
                                    {editable && !editing ? (
                                        <button
                                            className="btn btn-sm btn-danger float-right"
                                            onClick={() => store.deleteRow(rowIdx)}>
                                            Delete
                                        </button>
                                    ) : null}
                                    <span>
                                        {row.type} {row.id} not found
                                    </span>
                                </td>
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
