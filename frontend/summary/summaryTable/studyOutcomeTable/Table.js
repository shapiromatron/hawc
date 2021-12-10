import _ from "lodash";
import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Alert from "shared/components/Alert";
import Loading from "shared/components/Loading";
import SelectInput from "shared/components/SelectInput";

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

class EditCellForm extends Component {
    render() {
        const {store, rowIdx, colIdx} = this.props,
            typeChoices = store.rowTypeChoices,
            idChoices = store.rowIdChoices;
        return (
            <td>
                {colIdx === 0 ? (
                    <>
                        <div className="col-md-12">
                            <SelectInput
                                choices={typeChoices}
                                value={typeChoices[0].id}
                                handleSelect={value => console.log(value)}
                                label="Data type"
                            />
                        </div>
                        <div className="col-md-12">
                            <SelectInput
                                choices={idChoices}
                                value={idChoices[0].id}
                                handleSelect={value => console.log(value)}
                                label="Item"
                            />
                        </div>
                        <div className="col-md-12">
                            <button
                                className="btn btn-sm btn-primary"
                                onClick={() => store.updateRow(rowIdx)}>
                                Update
                            </button>
                            <button
                                className="btn btn-sm btn-light"
                                onClick={() => store.setEditRowIndex(null)}>
                                Cancel
                            </button>
                            <button
                                className="btn btn-sm btn-danger"
                                onClick={() => store.deleteRow(rowIdx)}>
                                Delete
                            </button>
                            <button
                                className="btn btn-sm btn-light"
                                onClick={() => store.moveRow(rowIdx, 1)}>
                                <i className="fa fa-arrow-up"></i>
                            </button>
                            <button
                                className="btn btn-sm btn-light"
                                onClick={() => store.moveRow(rowIdx, -1)}>
                                <i className="fa fa-arrow-down"></i>
                            </button>
                        </div>
                    </>
                ) : null}
            </td>
        );
    }
}
EditCellForm.propTypes = {
    store: PropTypes.object.isRequired,
    rowIdx: PropTypes.number.isRequired,
    colIdx: PropTypes.number.isRequired,
};

@observer
class Table extends Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchData();
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

        const {numColumns, settings, editColumnIndex, editRowIndex} = store;
        return (
            <table className="summaryTable table table-bordered table-sm">
                <thead>
                    <tr>
                        {settings.columns.map((col, idx) => {
                            return editColumnIndex === idx ? (
                                <th key={col.key}>EDIT</th>
                            ) : (
                                <th key={col.key} className="position-relative">
                                    {editable ? (
                                        <EditButton
                                            handleClick={() => store.setEditColumnIndex(idx)}
                                        />
                                    ) : null}
                                    {col.label}
                                </th>
                            );
                        })}
                    </tr>
                </thead>
                <tbody>
                    {settings.rows.map((row, rowIdx) => {
                        return (
                            <tr key={rowIdx}>
                                {_.range(0, numColumns).map(colIdx => {
                                    if (colIdx === editColumnIndex) {
                                        return <td key={colIdx}>EDIT COLUMN</td>;
                                    } else if (rowIdx === editRowIndex) {
                                        return (
                                            <EditCellForm
                                                key={colIdx}
                                                store={store}
                                                rowIdx={rowIdx}
                                                colIdx={colIdx}
                                            />
                                        );
                                    } else {
                                        return (
                                            <td
                                                key={colIdx}
                                                className={colIdx === 0 ? "position-relative" : ""}>
                                                {editable && colIdx === 0 ? (
                                                    <EditButton
                                                        handleClick={() =>
                                                            store.setEditRowIndex(rowIdx)
                                                        }
                                                    />
                                                ) : null}
                                                {row.type}-{row.id}-{colIdx}
                                            </td>
                                        );
                                    }
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
