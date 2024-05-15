import PropTypes from "prop-types";
import React, {Component} from "react";
import h from "shared/utils/helpers";

class CellTooltip extends Component {
    getRows() {
        const {x_filters, y_filters} = this.props.data;
        let rows = [];
        rows.push(
            ...x_filters.map((e, i) => {
                return (
                    <tr key={`x_filter_${i}`}>
                        <th>{h.titleCase(e.column)}</th>
                        <td>{e.value}</td>
                    </tr>
                );
            })
        );
        rows.push(
            ...y_filters.map((e, i) => {
                return (
                    <tr key={`y_filter_${i}`}>
                        <th>{h.titleCase(e.column)}</th>
                        <td>{e.value}</td>
                    </tr>
                );
            })
        );

        rows.push(
            <tr key="count">
                <th>Count</th>
                <td>{this.props.count}</td>
            </tr>
        );

        return rows;
    }
    render() {
        return (
            <table
                className="table table-sm table-bordered"
                style={{minWidth: 300, marginBottom: 0}}>
                <tbody>{this.getRows()}</tbody>
            </table>
        );
    }
}
CellTooltip.propTypes = {
    data: PropTypes.object,
    count: PropTypes.number,
};

class AxisTooltip extends Component {
    render() {
        const {filters} = this.props.data;
        return (
            <table
                className="table table-sm table-bordered"
                style={{minWidth: 300, marginBottom: 0}}>
                <tbody>
                    {filters.map((e, i) => {
                        return (
                            <tr key={i}>
                                <th>{h.titleCase(e.column)}</th>
                                <td>{e.value}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    }
}
AxisTooltip.propTypes = {
    data: PropTypes.object,
};

export {AxisTooltip, CellTooltip};
