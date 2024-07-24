import { inject, observer } from "mobx-react";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { ActionsTh, MoveRowTd } from "shared/components/EditableRowData";
import TextInput from "shared/components/TextInput";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";


const key = "boxes";

@inject("store")
@observer
class PrismaBoxesTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            { createNewSection } = this.props.store.subclass;

        return (
            <div>
                <h3>Boxes</h3>
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
                            <th>Text Formatting Style</th>
                            <th>Section</th>
                            <ActionsTh onClickNew={createNewSection} />
                        </tr>
                    </thead>
                    <tbody>{items.map((row, index) => this.renderRow(row, index))}</tbody>
                </table>
            </div>
        );
    }
    renderRow(row, index) {
        const {
            changeArraySettings,
            deleteArrayElement,
            getLinkingOptions,
        } = this.props.store.subclass;

        return (
            <tr key={index}>
                <td>
                    <TextInput
                        name={`${key}-name-${index}`}
                        value={row.name}
                        onChange={e => changeArraySettings(key, index, "name", e.target.value)}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${key}-width-${index}`}
                        onChange={e => changeArraySettings(key, index, "column", e.target.value)}
                        value={row.width}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${key}-height-${index}`}
                        value={row.height}
                        onChange={e => changeArraySettings(key, index, "header", e.target.value)}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${key}-border-width-${index}`}
                        value={row.border_width}
                        onChange={e => changeArraySettings(key, index, "border_width", e.target.value)}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${key}-rx-${index}`}
                        value={row.rx}
                        onChange={e => changeArraySettings(key, index, "rx", e.target.value)}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${key}-ry-${index}`}
                        value={row.ry}
                        onChange={e => changeArraySettings(key, index, "ry", e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-bg-color-${index}`}
                        className="col-md-12"
                        value={row.bg_color}
                        onChange={e => changeArraySettings(key, index, "bg_color", e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-border-color-${index}`}
                        className="col-md-12"
                        value={row.border_color}
                        onChange={e => changeArraySettings(key, index, "border_color", e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-font-color-${index}`}
                        className="col-md-12"
                        value={row.font_color}
                        onChange={e => changeArraySettings(key, index, "font_color", e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-text-style-${index}`}
                        className="col-md-12"
                        value={row.text_style}
                        onChange={e => changeArraySettings(key, index, "text_style", e.target.value)}
                    />
                </td>
                <td>
                    <SelectInput
                        name={`${key}-section-${index}`}
                        value={row.section}
                        handleSelect={value =>
                            changeArraySettings(key, index, "on_click_event", value)
                        }
                        multiple={false}
                        choices={getLinkingOptions("sections")}
                    />
                </td>
                <MoveRowTd
                    onDelete={() => deleteArrayElement(key, index)}
                />
            </tr>
        );
    }
}
PrismaBoxesTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaBoxesTable;
