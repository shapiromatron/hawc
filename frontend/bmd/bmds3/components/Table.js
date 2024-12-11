import PropTypes from "prop-types";
import React from "react";

const Table = function({label, extraClasses, colWidths, colNames, data, footer}) {
    return (
        <table className={`table table-sm ${extraClasses}`}>
            <colgroup>
                {colWidths.map((width, i) => (
                    <col key={i} width={`${width}%`} />
                ))}
            </colgroup>
            <thead>
                {label ? (
                    <tr className="bg-custom text-left">
                        <th colSpan={colWidths.length}>{label}</th>
                    </tr>
                ) : null}
                {colNames ? (
                    <tr className="bg-custom">
                        {colNames.map((name, i) => (
                            <th key={i}>{name}</th>
                        ))}
                    </tr>
                ) : null}
            </thead>
            <tbody>
                {data.map((row, i) => (
                    <tr key={i}>
                        {row.map((cell, j) => (
                            <td key={j}>{cell}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
            {footer ? (
                <tfoot>
                    <tr>
                        <td colSpan={colWidths.length}>{footer}</td>
                    </tr>
                </tfoot>
            ) : null}
        </table>
    );
};
Table.propTypes = {
    label: PropTypes.string,
    extraClasses: PropTypes.string.isRequired,
    colWidths: PropTypes.array.isRequired,
    colNames: PropTypes.array,
    data: PropTypes.array.isRequired,
    footer: PropTypes.node,
};

export default Table;
