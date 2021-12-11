import _ from "lodash";
import {toJS} from "mobx";
import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import Alert from "shared/components/Alert";
import Loading from "shared/components/Loading";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

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

class EditCellForm extends Component {
    render() {
        const {rowIdx, colIdx} = this.props;
        return (
            <td>
                <span>
                    CELL-{rowIdx}-{colIdx}
                </span>
            </td>
        );
    }
}
EditCellForm.propTypes = {
    store: PropTypes.object.isRequired,
    rowIdx: PropTypes.number.isRequired,
    colIdx: PropTypes.number.isRequired,
};

class EditRowForm extends Component {
    constructor(props) {
        super(props);
        const {store, rowIdx} = this.props;
        this.state = toJS(store.settings.rows[rowIdx]);
    }
    render() {
        const {store, rowIdx} = this.props,
            typeChoices = store.rowTypeChoices,
            idChoices = store.rowIdChoices;
        return (
            <td>
                <div className="col-md-12">
                    <SelectInput
                        choices={typeChoices}
                        value={this.state.type}
                        handleSelect={value => this.setState({type: value})}
                        label="Data type"
                    />
                </div>
                <div className="col-md-12">
                    <SelectInput
                        choices={idChoices}
                        value={this.state.id}
                        handleSelect={value => this.setState({id: parseInt(value)})}
                        label="Item"
                    />
                </div>
                <div className="col-md-12 text-center">
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={() => store.updateRow(rowIdx, this.state)}>
                            Update
                        </button>
                        <button
                            className="btn btn-sm btn-light"
                            onClick={() => store.setEditRowIndex(null)}>
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
            </td>
        );
    }
}
EditRowForm.propTypes = {
    store: PropTypes.object.isRequired,
    rowIdx: PropTypes.number.isRequired,
};

@observer
class EditColumnForm extends Component {
    constructor(props) {
        super(props);
        const {store, colIdx} = this.props;
        this.state = toJS(store.settings.columns[colIdx]);
    }
    render() {
        const {store, colIdx} = this.props;
        return (
            <td>
                <div className="col-md-12">
                    <TextInput
                        onChange={e => this.setState({label: e.target.value})}
                        name="label"
                        value={this.state.label}
                        label="Label"
                    />
                </div>
                <div className="col-md-12">
                    <SelectInput
                        choices={robAttributeChoices}
                        handleSelect={value => this.setState({attribute: value})}
                        value={this.state.attribute}
                        label="Attribute"
                    />
                </div>
                <div className="col-md-12 text-center">
                    <div className="btn-group">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={() => store.updateColumn(colIdx, this.state)}>
                            Update
                        </button>
                        <button
                            className="btn btn-sm btn-light"
                            onClick={() => store.setEditColumnIndex(null)}>
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
            </td>
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
                                <EditColumnForm key={col.key} store={store} colIdx={idx} />
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
                                    if (colIdx == 0 && rowIdx === editRowIndex) {
                                        return (
                                            <EditRowForm
                                                key={colIdx}
                                                store={store}
                                                rowIdx={rowIdx}
                                            />
                                        );
                                    } else if (
                                        colIdx === editColumnIndex ||
                                        rowIdx === editRowIndex
                                    ) {
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
