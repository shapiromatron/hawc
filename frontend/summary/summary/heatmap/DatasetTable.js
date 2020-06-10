import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";
import _ from "lodash";
import h from "shared/utils/helpers";

import {autorun, toJS} from "mobx";

class DatasetTable2 {
    /*
    A DatasetTable is the detailed table below a heatmap which shows details on a given cell when
    selected or filtered.
    */
    constructor(store) {
        this.store = store;
        this.table = null;
        autorun(() => {
            this.updateTableBody(toJS(this.store.selectedTableData));
        });
    }

    renderTable(el, parentEl) {
        const svgHeight =
                h.getHawcContentSize().height -
                $(parentEl)
                    .parent()
                    .height(),
            {table_fields} = this.store.settings;

        // Create detail container
        let container = el
            .append("div")
            .attr("class", "exp_heatmap_container")
            .style("width", "100%")
            .style("height", `${Math.max(svgHeight, 200)}px`)
            .style("overflow", "auto");

        // Create detail table
        let table = container.append("table").attr("class", "table table-striped table-bordered");

        // Create the table header
        table
            .append("thead")
            .append("tr")
            .selectAll("th")
            .data(table_fields)
            .enter()
            .append("th")
            .text(d => d);

        // Fill in table body
        table.append("tbody");

        this.table = table;
    }

    updateTableBody(data) {
        const {table_fields} = this.store.settings;
        this.table
            .select("tbody")
            .selectAll("tr")
            .remove();

        if (!data) {
            return;
        }

        this.table
            .select("tbody")
            .selectAll("tr")
            .data(data)
            .enter()
            .append("tr")
            .selectAll("td")
            .data(d => table_fields.map(e => d[e]))
            .enter()
            .append("td")
            .text(d => d);
    }
}

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
