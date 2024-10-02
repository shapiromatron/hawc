import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import {NULL_VALUE} from "summary/summary/constants";

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
                        <col width="45%" />
                        <col width="45%" />
                        <col width="10%" />
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
                />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const {
            changeArraySettings,
            toggleArrowStyling,
            getArrowOptions,
        } = this.props.store.subclass;
        return (
            <tr>
                <td colSpan="100%">
                    <div className="border my-2 p-2 pb-3 edit-form-background ">
                        <div className="form-row my-2 mx-2 pad-form">
                            <SelectInput
                                name={`${key}-source-${index}`}
                                value={row.src}
                                label="Source"
                                handleSelect={(value, label) => {
                                    changeArraySettings(key, index, "src", value);
                                }}
                                multiple={false}
                                choices={getArrowOptions()}
                            />
                            <SelectInput
                                name={`${key}-destination-${index}`}
                                value={row.dst}
                                label="Destination"
                                handleSelect={(value, label) => {
                                    changeArraySettings(key, index, "dst", value);
                                }}
                                multiple={false}
                                choices={getArrowOptions()}
                            />
                            <CheckboxInput
                                name={`${key}-toggle-styling-${index}`}
                                checked={row.styling != null}
                                label="Override default formatting"
                                onChange={e => {
                                    toggleArrowStyling(key, index, e.target.checked);
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

    renderStyleOptions(key, row, index) {
        const {changeStylingSettings, getArrowTypes} = this.props.store.subclass;
        return (
            <div className="form-row">
                <IntegerInput
                    name={`${key}-width-${index}`}
                    value={row.styling.width}
                    label="Width"
                    onChange={e =>
                        changeStylingSettings(key, index, "width", parseInt(e.target.value))
                    }
                />
                <SelectInput
                    name={`${key}-type-${index}`}
                    value={row.styling.type}
                    label="Type"
                    handleSelect={value =>
                        changeStylingSettings(key, index, "type", parseInt(value))
                    }
                    choices={getArrowTypes()}
                />
                <TextInput
                    name={`${key}-color-${index}`}
                    value={row.styling.color}
                    label="Color"
                    onChange={e => changeStylingSettings(key, index, "color", e.target.value)}
                    type="color"
                />
                <CheckboxInput
                    name={`${key}-force-vertical-${index}`}
                    checked={row.styling.force_vertical}
                    label="Force vertical orientation"
                    onChange={e =>
                        changeStylingSettings(key, index, "force_vertical", e.target.checked)
                    }
                />
            </div>
        );
    }
}
PrismaArrowsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaArrowsTable;
