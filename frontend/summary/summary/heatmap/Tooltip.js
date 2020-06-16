import React, {Component} from "react";
import PropTypes from "prop-types";

class Tooltip extends Component {
    render() {
        const style = {
            position: "absolute",
            backgroundColor: "white",
        };

        let tooltip = null;

        if (this.props.type == "cell") tooltip = this.renderCellTooltip();
        if (this.props.type == "axis") tooltip = this.renderAxisTooltip();

        return (
            <table className="table table-condensed table-bordered" style={style}>
                <tbody>{tooltip}</tbody>
            </table>
        );
    }

    renderCellTooltip() {
        const {x_filters, y_filters} = this.props.data,
            count = this.props.data.rows.length;
        let rows = [];
        rows.push(
            ...x_filters.map((e, i) => {
                return (
                    <tr key={`x_filter_${i}`}>
                        <td>{e.column}</td>
                        <td>{e.value}</td>
                    </tr>
                );
            })
        );
        rows.push(
            ...y_filters.map((e, i) => {
                return (
                    <tr key={`y_filter_${i}`}>
                        <td>{e.column}</td>
                        <td>{e.value}</td>
                    </tr>
                );
            })
        );

        rows.push(
            <tr key="count">
                <td>Count</td>
                <td>{count}</td>
            </tr>
        );

        return rows;
    }
    renderAxisTooltip() {
        const {filters} = this.props.data;
        let rows = [];

        rows.push(
            ...filters.map((e, i) => {
                return (
                    <tr key={`filter_${i}`}>
                        <td>{e.column}</td>
                        <td>{e.value}</td>
                    </tr>
                );
            })
        );

        return rows;
    }
}
Tooltip.propTypes = {
    data: PropTypes.object,
    type: PropTypes.string,
};

export default Tooltip;
