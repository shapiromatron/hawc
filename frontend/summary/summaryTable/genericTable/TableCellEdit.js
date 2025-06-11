import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import {QuickEditCell} from "./EditCell";
import {getCellExcelName} from "./common";

@observer
class TableCellEdit extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isHovering: false,
        };
    }
    render() {
        const {cell, store} = this.props,
            {quickEditCell} = store,
            isQuickEditCell = quickEditCell === cell,
            elType = cell.header ? "th" : "td",
            {isHovering} = this.state,
            attrs = {
                className: "position-relative",
                rowSpan: cell.row_span,
                colSpan: cell.col_span,
                onClick: e => {
                    if (
                        !e.target.classList.contains("btn") &&
                        !e.target.classList.contains("fa-edit")
                    ) {
                        store.selectCellEdit(cell, true);
                    }
                },
                onMouseEnter: () => this.setState({isHovering: true}),
                onMouseLeave: () => this.setState({isHovering: false}),
            },
            children = [
                <button
                    className="btn btn-light btn-sm float-right-absolute"
                    style={{display: isHovering && !isQuickEditCell ? "inline" : "none"}}
                    key={0}
                    onClick={() => {
                        store.selectCellEdit(cell, false);
                    }}>
                    <i className="fa fa-edit mr-1"></i>Edit {getCellExcelName(cell)}
                </button>,
                isQuickEditCell ? (
                    <QuickEditCell key={1} store={store} />
                ) : (
                    <div
                        key={1}
                        style={{minHeight: 25}}
                        dangerouslySetInnerHTML={{__html: cell.quill_text}}></div>
                ),
            ];
        return React.createElement(elType, attrs, children);
    }
}
TableCellEdit.propTypes = {
    store: PropTypes.object.isRequired,
    cell: PropTypes.object.isRequired,
};

export default TableCellEdit;
