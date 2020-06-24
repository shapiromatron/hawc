import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import {NULL_VALUE} from "../constants";

const pillItems = function(text, delimiter) {
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
            <span key={i} className="label" style={{marginRight: 3}}>
                {item}
            </span>
        ));
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
        const {store, row, field} = this.props,
            showButton = () => this.setState({isHovering: true}),
            hideButton = () => this.setState({isHovering: false});

        return (
            <td onMouseEnter={showButton} onMouseLeave={hideButton}>
                <a href={store.getDetailUrl(field.on_click_event, row)}>
                    {pillItems(row[field.column], field.delimiter)}
                </a>
                {this.state.isHovering ? (
                    <button
                        className="btn btn-mini pull-right"
                        onClick={() => {
                            store.showModalClick(field.on_click_event, row);
                            hideButton();
                        }}
                        title="View additional information">
                        <i className="icon-eye-open"></i>
                    </button>
                ) : null}
            </td>
        );
    }
}
InteractiveCell.propTypes = {
    store: PropTypes.object.isRequired,
    row: PropTypes.object.isRequired,
    field: PropTypes.object.isRequired,
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
            data = this.props.store.getTableData;

        return (
            <div>
                <table className="table table-striped table-bordered">
                    <thead>
                        <tr>
                            {table_fields.map((name, i) => (
                                <th key={i}>{name.column}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>{data.map((row, i) => this.renderRow(row, i, table_fields))}</tbody>
                </table>
            </div>
        );
    }
    renderRow(row, index, table_fields) {
        return (
            <tr key={index}>
                {table_fields.map((field, i2) => {
                    return field.on_click_event === NULL_VALUE ? (
                        <td key={i2}>{pillItems(row[field.column], field.delimiter)}</td>
                    ) : (
                        <InteractiveCell
                            key={i2}
                            store={this.props.store}
                            row={row}
                            field={field}
                        />
                    );
                })}
            </tr>
        );
    }
}
DatasetTable.propTypes = {
    store: PropTypes.object,
};

export default DatasetTable;
