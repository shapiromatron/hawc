import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

@observer
class TableCell extends Component {
    render() {
        const {cell} = this.props,
            elType = cell.header ? "th" : "td",
            attrs = {
                rowSpan: cell.row_span,
                colSpan: cell.col_span,
            };

        return React.createElement(
            elType,
            attrs,
            <div dangerouslySetInnerHTML={{__html: cell.quill_text}}></div>
        );
    }
}
TableCell.propTypes = {
    cell: PropTypes.object.isRequired,
};

export default TableCell;
