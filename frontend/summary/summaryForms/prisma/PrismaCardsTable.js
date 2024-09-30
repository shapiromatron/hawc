import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionsTh, EditableRow, MoveRowTd} from "shared/components/EditableRowData";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

const key = "cards";

@inject("store")
@observer
class PrismaCardsTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewCard} = this.props.store.subclass;

        return (
            <div>
                <h3>Cards</h3>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="45%" />
                        <col width="45%" />
                        <col width="10%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Tag</th>
                            <ActionsTh onClickNew={createNewCard} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((row, index) => {
                            return (
                                <CardsRow
                                    row={row}
                                    index={index}
                                    key={index}
                                    initiallyEditable={row.label == ""}
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
class CardsRow extends EditableRow {
    renderViewRow(row, index) {
        const {deleteArrayElement} = this.props.store.subclass;

        return (
            <tr>
                <td>{row.label}</td>
                <td>{row.tag}</td>
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
                            <IntegerInput
                                name={`${key}-width-${index}`}
                                onChange={e =>
                                    changeArraySettings(key, index, "width", e.target.value)
                                }
                                label="Width"
                                value={row.width}
                            />
                            <IntegerInput
                                name={`${key}-height-${index}`}
                                value={row.height}
                                label="Height"
                                onChange={e =>
                                    changeArraySettings(key, index, "height", e.target.value)
                                }
                            />
                            <IntegerInput
                                name={`${key}-border-width-${index}`}
                                value={row.border_width}
                                label="Border Width"
                                onChange={e =>
                                    changeArraySettings(key, index, "border_width", e.target.value)
                                }
                            />
                            <IntegerInput
                                name={`${key}-rx-${index}`}
                                value={row.rx}
                                label="rx"
                                onChange={e =>
                                    changeArraySettings(key, index, "rx", e.target.value)
                                }
                            />
                            <IntegerInput
                                name={`${key}-ry-${index}`}
                                value={row.ry}
                                label="ry"
                                onChange={e =>
                                    changeArraySettings(key, index, "ry", e.target.value)
                                }
                            />
                            <TextInput
                                name={`${key}-bg-color-${index}`}
                                value={row.bg_color}
                                label="Background Color"
                                onChange={e =>
                                    changeArraySettings(key, index, "bg_color", e.target.value)
                                }
                            />
                            <TextInput
                                name={`${key}-border-color-${index}`}
                                value={row.border_color}
                                label="Border Color"
                                onChange={e =>
                                    changeArraySettings(key, index, "border_color", e.target.value)
                                }
                            />
                            <TextInput
                                name={`${key}-font-color-${index}`}
                                value={row.font_color}
                                label="Font Color"
                                onChange={e =>
                                    changeArraySettings(key, index, "font_color", e.target.value)
                                }
                            />
                            <SelectInput
                                name={`${key}-box-${index}`}
                                value={row.box}
                                label="Box"
                                handleSelect={value =>
                                    changeArraySettings(key, index, "box", value)
                                }
                                multiple={false}
                                choices={getLinkingOptions("boxes")}
                            />
                            <SelectInput
                                name={`${key}-tag-${index}`}
                                value={row.tag}
                                label="Add references related to this tag, search, or import"
                                handleSelect={value =>
                                    changeArraySettings(key, index, "tag", value)
                                }
                                multiple={false}
                                choices={getFilterOptions()}
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
PrismaCardsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaCardsTable;
