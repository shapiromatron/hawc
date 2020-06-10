import React, {Component} from "react";
import PropTypes from "prop-types";
import {observer} from "mobx-react";

@observer
class DatasetTable extends Component {
    render() {
        const {table_fields} = this.props.store.settings,
            data = this.props.store.selectedTableData;

        return (
            <div className="exp_heatmap_container">
                <table className="table table-striped table-bordered">
                    <thead>
                        <tr>
                            {table_fields.map((name, i) => (
                                <th key={i}>{name}</th>
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
                {table_fields.map((name, i2) => (
                    <td key={i2}>{row[name]}</td>
                ))}
            </tr>
        );
    }
}
DatasetTable.propTypes = {
    store: PropTypes.object,
};

export default DatasetTable;
