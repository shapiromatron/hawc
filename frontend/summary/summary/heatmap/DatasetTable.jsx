import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

import {getAction, getDetailUrl, showAsModal} from "../../interactivity/actions";

const pillItems = function (text, delimiter) {
        if (!delimiter) {
            return text;
        }
        if (!text) {
            return "";
        }
        return text
            .toString()
            .split(delimiter)
            .map((item, i) => (
                <span key={i} className="badge badge-secondary mr-1">
                    {item}
                </span>
            ));
    },
    getInteractivityMap = function (columns) {
        const map = {};
        columns.forEach(col => {
            const action = getAction(col.on_click_event);
            if (action) {
                map[col.column] = action;
            }
        });
        return map;
    };

@observer
class InteractiveCell extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isHovering: false,
        };
    }

    render() {
        const {row, field, extension} = this.props,
            {isHovering} = this.state,
            showButton = () => this.setState({isHovering: true}),
            hideButton = () => this.setState({isHovering: false});

        return (
            <td onMouseEnter={showButton} onMouseLeave={hideButton}>
                {extension.modal ? (
                    <button
                        style={{opacity: isHovering ? 1 : 0}}
                        className="btn btn-sm float-right"
                        onClick={() => showAsModal(extension, row)}
                        title="View additional information">
                        <i className="fa fa-external-link"></i>
                    </button>
                ) : null}
                <a href={getDetailUrl(extension, row)}>
                    {pillItems(row[field.column], field.delimiter)}
                </a>
            </td>
        );
    }
}
InteractiveCell.propTypes = {
    store: PropTypes.object.isRequired,
    row: PropTypes.object.isRequired,
    field: PropTypes.object.isRequired,
    extension: PropTypes.object.isRequired,
};

@inject("store")
@observer
class DatasetTable extends Component {
    constructor(props) {
        super(props);
        this.renderRow = this.renderRow.bind(this);
    }
    render() {
        const {table_fields} = this.props.store.settings,
            interactivity = getInteractivityMap(table_fields),
            data = this.props.store.getTableData.data;

        return (
            <div className="mt-2" style={{maxHeight: "50vh", overflow: "auto"}}>
                <table className="table table-striped table-bordered">
                    <thead>
                        <tr>
                            {table_fields.map((name, i) => (
                                <th key={i}>
                                    {name.header ? name.header : h.titleCase(name.column)}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, i) => this.renderRow(row, i, table_fields, interactivity))}
                    </tbody>
                </table>
            </div>
        );
    }
    renderRow(row, index, table_fields, interactivity) {
        return (
            <tr key={index}>
                {table_fields.map((field, i2) => {
                    const extension = interactivity[field.column];
                    if (extension) {
                        return (
                            <InteractiveCell
                                key={i2}
                                store={this.props.store}
                                row={row}
                                field={field}
                                extension={extension}
                            />
                        );
                    } else {
                        return <td key={i2}>{pillItems(row[field.column], field.delimiter)}</td>;
                    }
                })}
            </tr>
        );
    }
}
DatasetTable.propTypes = {
    store: PropTypes.object,
};

export default DatasetTable;
