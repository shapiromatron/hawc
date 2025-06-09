import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import {
    ActionsTh,
    MoveRowTd,
    moveArrayElementDown,
    moveArrayElementUp,
} from "shared/components/EditableRowData";
import TextInput from "shared/components/TextInput";

import {PrismaEditableRow} from "./PrismaEditableRow";

const key = "sections";

@inject("store")
@observer
class PrismaSectionsTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewSection} = this.props.store.subclass;
        return (
            <div>
                <h3>Sections</h3>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="85%" />
                        <col width="15%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <ActionsTh onClickNew={createNewSection} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((row, index) => {
                            return (
                                <SectionsRow
                                    row={row}
                                    index={index}
                                    key={index}
                                    initiallyEditable={row.label == ""}
                                    editStyles={row.use_style_overrides}
                                />
                            );
                        })}
                    </tbody>
                </table>
            </div>
        );
    }
}

@inject("store")
@observer
class SectionsRow extends PrismaEditableRow {
    renderViewRow(row, index) {
        const {deleteArrayElement} = this.props.store.subclass;

        return (
            <tr>
                <td>{row.label}</td>
                <MoveRowTd
                    onDelete={() => deleteArrayElement(key, index)}
                    onEdit={() => this.setState({edit: true})}
                    onMoveUp={() =>
                        moveArrayElementUp(this.props.store.subclass.settings[key], index)
                    }
                    onMoveDown={() =>
                        moveArrayElementDown(this.props.store.subclass.settings[key], index)
                    }
                />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const {changeArraySettings, toggleStyling} = this.props.store.subclass;
        return (
            <tr>
                <td colSpan="100%">
                    <div className="border my-2 p-2 pb-3 edit-form-background ">
                        <div className="form-row my-2 mx-2 pad-form">
                            <div className="col-6">
                                <TextInput
                                    name={`${key}-name-${index}`}
                                    value={row.label}
                                    label="Name"
                                    onChange={e =>
                                        changeArraySettings(key, index, "label", e.target.value)
                                    }
                                />
                            </div>
                            <div className="col-6">
                                <p className="mb-3">&nbsp;</p>
                                <CheckboxInput
                                    name={`${key}-toggle-styling-${index}`}
                                    checked={row.use_style_overrides}
                                    label="Override default formatting"
                                    onChange={e => {
                                        toggleStyling(key, index, e.target.checked);
                                        this.setState({edit_styles: e.target.checked});
                                    }}
                                />
                            </div>
                            {this.state.edit_styles
                                ? this.renderStyleOptions(key, row, index)
                                : null}
                        </div>
                        <div className="form-row justify-content-center">
                            <button
                                className="btn btn-primary mx-2 py-2"
                                type="button"
                                style={{width: "15rem", padding: "0.7rem"}}
                                onClick={() => this.setState({edit: false})}>
                                Close
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        );
    }
}
PrismaSectionsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaSectionsTable;
