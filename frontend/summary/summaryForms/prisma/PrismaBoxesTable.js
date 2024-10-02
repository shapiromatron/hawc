import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import {PrismaEditableRow} from "./PrismaEditableRow";

const key = "boxes";

@inject("store")
@observer
class PrismaBoxesTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewBox} = this.props.store.subclass;

        return (
            <div>
                <h3>Boxes</h3>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="45%" />
                        <col width="45%" />
                        <col width="10%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Section</th>
                            <ActionsTh onClickNew={createNewBox} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((row, index) => {
                            return (
                                <BoxesRow
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
class BoxesRow extends PrismaEditableRow {
    renderViewRow(row, index) {
        const {deleteArrayElement, sectionMapping} = this.props.store.subclass;

        return (
            <tr>
                <td>{row.label}</td>
                <td>{sectionMapping[row.section]}</td>
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
                    <div className="border my-2 p-2 pb-3 edit-form-background ">
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
                                name={`${key}-section-${index}`}
                                value={row.section}
                                label="Section"
                                handleSelect={(value, label) => {
                                    changeArraySettings(key, index, "section", value);
                                }}
                                multiple={false}
                                choices={getLinkingOptions("sections")}
                            />
                            <SelectInput
                                name={`${key}-tag-${index}`}
                                value={row.tag}
                                label="Add references related to this tag, search, or import"
                                handleSelect={(value, label) => {
                                    changeArraySettings(key, index, "tag", value);
                                }}
                                multiple={true}
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
PrismaBoxesTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaBoxesTable;
