import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionsTh, BaseEditableRow, MoveRowTd} from "shared/components/EditableRowData";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

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
                    {/* <colgroup>
                    <col width="25%" />
                    <col width="25%" />
                    <col width="20%" />
                    <col width="20%" />
                    <col width="10%" />
                </colgroup> */}
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Width</th>
                            <th>Height</th>
                            <th>Border Width</th>
                            <th>rx</th>
                            <th>ry</th>
                            <th>Background Color</th>
                            <th>Border Color</th>
                            <th>Font Color</th>
                            <th>Box</th>
                            <th>Tag</th>
                            <ActionsTh onClickNew={createNewBulletedList} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((row, index) => {
                            return <BulletedListsRow row={row} index={index} key={index} />;
                        })}
                    </tbody>
                </table>
            </div>
        );
    }
}

@inject("store")
@observer
class BulletedListsRow extends BaseEditableRow {
    renderViewRow(row, index) {
        const {deleteArrayElement} = this.props.store.subclass;

        return (
            <tr>
                <td>{row.name}</td>
                <td>{row.width}</td>
                <td>{row.height}</td>
                <td>{row.border_width}</td>
                <td>{row.rx}</td>
                <td>{row.ry}</td>
                <td>{row.bg_color}</td>
                <td>{row.border_color}</td>
                <td>{row.font_color}</td>
                <td>{row.box}</td>
                <td>{row.tag}</td>
                <MoveRowTd
                    onDelete={() => deleteArrayElement(key, index)}
                    onEdit={() => this.setState({edit: true})}
                />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const {changeArraySettings, getLinkingOptions, getTagOptions} = this.props.store.subclass;
        return (
            <tr>
                <td colSpan="100%">
                    <div className="border my-2 p-2 pb-3 edit-form-background ">
                        <div className="form-row my-2 mx-2">
                            <TextInput
                                name={`${key}-name-${index}`}
                                value={row.name}
                                label="Name"
                                onChange={e =>
                                    changeArraySettings(key, index, "name", e.target.value)
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
                                label="Tag related to data in this list"
                                handleSelect={value =>
                                    changeArraySettings(key, index, "tag", value)
                                }
                                multiple={false}
                                choices={getTagOptions()}
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
PrismaBulletedListsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaBulletedListsTable;
