import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionsTh, EditableRow, MoveRowTd} from "shared/components/EditableRowData";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

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
                                    initiallyEditable={row.source == ""}
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
class ArrowsRow extends EditableRow {
    renderViewRow(row, index) {
        const {deleteArrayElement} = this.props.store.subclass;

        return (
            <tr>
                <td>{row.source}</td>
                <td>{row.dest}</td>
                <MoveRowTd
                    onDelete={() => deleteArrayElement(key, index)}
                    onEdit={() => this.setState({edit: true})}
                />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const {changeArraySettings, getArrowOptions} = this.props.store.subclass;
        return (
            <tr>
                <td colSpan="100%">
                    <div className="border my-2 p-2 pb-3 edit-form-background ">
                        <div className="form-row my-2 mx-2 pad-form">
                            <SelectInput
                                name={`${key}-source-${index}`}
                                value={row.source}
                                label="Source"
                                handleSelect={value =>
                                    changeArraySettings(key, index, "source", value)
                                }
                                multiple={false}
                                choices={getArrowOptions()}
                            />
                            <SelectInput
                                name={`${key}-dest-${index}`}
                                value={row.dest}
                                label="Destination"
                                handleSelect={value =>
                                    changeArraySettings(key, index, "dest", value)
                                }
                                multiple={false}
                                choices={getArrowOptions()}
                            />
                            <IntegerInput
                                name={`${key}-width-${index}`}
                                value={row.width}
                                label="Width"
                                onChange={e =>
                                    changeArraySettings(key, index, "width", e.target.value)
                                }
                            />
                            <SelectInput
                                name={`${key}-type-${index}`}
                                value={row.type}
                                label="Type"
                                handleSelect={value =>
                                    changeArraySettings(key, index, "type", value)
                                }
                                multiple={false}
                                choices={[{id: 1, label: "test"}]} // TODO: define choices for arrow types
                            />
                            <TextInput
                                name={`${key}-color-${index}`}
                                value={row.color}
                                label="Color"
                                onChange={e =>
                                    changeArraySettings(key, index, "color", e.target.value)
                                }
                            />
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
PrismaArrowsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaArrowsTable;
