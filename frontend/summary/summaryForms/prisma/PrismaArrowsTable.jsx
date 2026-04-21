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
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import wrapRow from "shared/components/WrapRow";
import {NULL_VALUE} from "summary/summary/constants";

import {PrismaEditableRow} from "./PrismaEditableRow";

const key = "arrows";

@inject("store")
@observer
class PrismaArrowsTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewArrow} = this.props.store.subclass;

        return (
            <div>
                <h3>Arrows</h3>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="50%" />
                        <col width="35%" />
                        <col width="15%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Source</th>
                            <th>Destination</th>
                            <ActionsTh onClickNew={createNewArrow} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((row, index) => {
                            return (
                                <ArrowsRow
                                    row={row}
                                    index={index}
                                    key={index}
                                    initiallyEditable={row.src == NULL_VALUE}
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
class ArrowsRow extends PrismaEditableRow {
    renderViewRow(row, index) {
        const {deleteArrayElement, arrowMapping} = this.props.store.subclass;
        return (
            <tr>
                <td>{arrowMapping[row.src]}</td>
                <td>{arrowMapping[row.dst]}</td>
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
        const {changeArraySettings, toggleStyling, getArrowOptions} = this.props.store.subclass;
        return (
            <tr>
                <td colSpan="100%">
                    <div className="border my-2 p-2 pb-3 edit-form-background ">
                        {wrapRow(
                            [
                                <SelectInput
                                    key={`${key}-source-${index}`}
                                    name={`${key}-source-${index}`}
                                    value={row.src}
                                    label="Source"
                                    handleSelect={value =>
                                        changeArraySettings(key, index, "src", value)
                                    }
                                    multiple={false}
                                    choices={getArrowOptions}
                                />,
                                <SelectInput
                                    key={`${key}-source-${index}`}
                                    name={`${key}-destination-${index}`}
                                    value={row.dst}
                                    label="Destination"
                                    handleSelect={value =>
                                        changeArraySettings(key, index, "dst", value)
                                    }
                                    multiple={false}
                                    choices={getArrowOptions}
                                />,
                                <div key="toggle-style">
                                    <p className="mb-3">&nbsp;</p>
                                    <CheckboxInput
                                        key={`${key}-source-${index}`}
                                        name={`${key}-toggle-styling-${index}`}
                                        checked={row.use_style_overrides}
                                        label="Override default formatting"
                                        onChange={e => {
                                            toggleStyling(key, index, e.target.checked);
                                            this.setState({edit_styles: e.target.checked});
                                        }}
                                    />
                                </div>,
                            ],
                            "form-row my-2 mx-2 pad-form"
                        )}
                        {this.state.edit_styles && this.renderStyleOptions(key, row, index)}
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

    renderStyleOptions(key, row, index) {
        const {changeStylingSettings, getArrowTypes} = this.props.store.subclass;
        return (
            <>
                {wrapRow(
                    [
                        <IntegerInput
                            key={`${key}-width-${index}`}
                            name={`${key}-width-${index}`}
                            value={row.styles.width}
                            label="Width"
                            onChange={e =>
                                changeStylingSettings(key, index, "width", parseInt(e.target.value))
                            }
                        />,
                        <SelectInput
                            key={`${key}-type-${index}`}
                            name={`${key}-type-${index}`}
                            value={row.styles.arrow_type}
                            label="Type"
                            handleSelect={value =>
                                changeStylingSettings(key, index, "arrow_type", parseInt(value))
                            }
                            choices={getArrowTypes}
                        />,
                        <TextInput
                            key={`${key}-color-${index}`}
                            name={`${key}-color-${index}`}
                            value={row.styles.color}
                            label="Color"
                            onChange={e =>
                                changeStylingSettings(key, index, "color", e.target.value)
                            }
                            type="color"
                        />,
                        <div key="force-vertical">
                            <p className="mb-3">&nbsp;</p>
                            <CheckboxInput
                                key={`${key}-force-vertical-${index}`}
                                name={`${key}-force-vertical-${index}`}
                                checked={row.styles.force_vertical}
                                label="Force vertical orientation"
                                onChange={e =>
                                    changeStylingSettings(
                                        key,
                                        index,
                                        "force_vertical",
                                        e.target.checked
                                    )
                                }
                            />
                        </div>,
                    ],
                    "form-row my-2 mx-2 pad-form"
                )}
            </>
        );
    }
}
PrismaArrowsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaArrowsTable;
