import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import {PrismaEditableRow} from "./PrismaEditableRow";

const key = "bulleted_lists";

@inject("store")
@observer
class PrismaBulletedListsTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewBulletedList} = this.props.store.subclass;

        return (
            <div>
                <h3>Bulleted Lists</h3>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="30%" />
                        <col width="30%" />
                        <col width="30%" />
                        <col width="10%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Box</th>
                            <th>Tag</th>
                            <ActionsTh onClickNew={createNewBulletedList} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((row, index) => {
                            return (
                                <BulletedListsRow
                                    row={row}
                                    index={index}
                                    key={index}
                                    initiallyEditable={row.label == ""}
                                    editStyles={row.styling != null}
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
class BulletedListsRow extends PrismaEditableRow {
    renderViewRow(row, index) {
        const {deleteArrayElement} = this.props.store.subclass;

        return (
            <tr>
                <td>{row.label}</td>
                <td>{row.box_display}</td>
                <td>{row.tag_display}</td>
                <MoveRowTd
                    onDelete={() => deleteArrayElement(key, index)}
                    onEdit={() => this.setState({edit: true})}
                />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const {
            changeArraySettings,
            toggleStyling,
            getLinkingOptions,
            getFilterOptions,
        } = this.props.store.subclass;
        return (
            <tr>
                <td colSpan="100%">
                    <div className="border my-2 p-2 pb-3 edit-form-background">
                        <div className="form-row my-2 mx-2 pad-form">
                            <TextInput
                                name={`${key}-name-${index}`}
                                value={row.label}
                                label="Name"
                                onChange={e =>
                                    changeArraySettings(key, index, "label", e.target.value)
                                }
                            />
                            <SelectInput
                                name={`${key}-box-${index}`}
                                value={row.box}
                                label="Box"
                                handleSelect={(value, label) => {
                                    changeArraySettings(key, index, "box", value);
                                    changeArraySettings(key, index, "box_display", label);
                                }}
                                multiple={false}
                                choices={getLinkingOptions("boxes")}
                            />
                            <SelectInput
                                name={`${key}-tag-${index}`}
                                value={row.tag}
                                label="Add references related to this tag, search, or import"
                                handleSelect={(value, label) => {
                                    changeArraySettings(key, index, "tag", value);
                                }}
                                multiple={false}
                                choices={getFilterOptions()}
                            />
                            <CheckboxInput
                                name={`${key}-toggle-styling-${index}`}
                                checked={row.styling != null}
                                label="Override default formatting"
                                onChange={e => {
                                    toggleStyling(key, index, e.target.checked);
                                    this.setState({edit_styles: e.target.checked});
                                }}
                            />
                            {this.state.edit_styles && this.renderStyleOptions(key, row, index)}
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
PrismaBulletedListsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaBulletedListsTable;
