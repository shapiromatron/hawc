import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";

import {getCellExcelName} from "./common";
import {QuickEditCell} from "./EditCell";

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
                    className="float-right btn btn-light btn-sm"
                    style={{opacity: isHovering && !isQuickEditCell ? 1 : 0}}
                    key={0}
                    onClick={() => {
                        store.selectCellEdit(cell, false);
                    }}>
                    <i className="fa fa-edit mr-1"></i>Edit {getCellExcelName(cell)}
                </button>,
                isQuickEditCell ? (
                    <QuickEditCell key={1} store={store} />
                ) : (
                    <div key={1} dangerouslySetInnerHTML={{__html: cell.quill_text}}></div>
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
