import { inject, observer } from "mobx-react";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { ActionsTh, MoveRowTd } from "shared/components/EditableRowData";
import HelpTextPopup from "shared/components/HelpTextPopup";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import { HelpText } from "./common";

const key = "filter_widgets";

@inject("store")
@observer
class PrismaSectionsTable extends Component {
    render() {
        const items = this.props.store.subclass.settings["sections"]

        return (
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
                    </tr>
                </thead>
                <tbody>{items.map((row, index) => this.renderRow(row, index))}</tbody>
            </table>
        );
    }
    renderRow(row, index) {
        const {
            getColumnsOptionsWithNull,
            changeArraySettings,
            moveArrayElementUp,
            moveArrayElementDown,
            deleteArrayElement,
            getInteractivityOptions,
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
                    <SelectInput
                        name={`${key}-width-${index}`}
                        choices={getColumnsOptionsWithNull}
                        multiple={false}
                        handleSelect={value => changeArraySettings(key, index, "column", value)}
                        value={row.width}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-height-${index}`}
                        value={row.height}
                        onChange={e => changeArraySettings(key, index, "header", e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-border-width-${index}`}
                        className="col-md-12"
                        value={row.border_width}
                        onChange={e => changeArraySettings(key, index, "border_width", e.target.value)}
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
            </tr>
        );
    }
}
PrismaSectionsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaSectionsTable;
