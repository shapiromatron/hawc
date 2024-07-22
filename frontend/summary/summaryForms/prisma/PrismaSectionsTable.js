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
        const items = this.props.store.subclass.settings[key],
            { createNewFilterWidget } = this.props.store.subclass;

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
                        value={row.header}
                        onChange={e => changeArraySettings(key, index, "name", e.target.value)}
                    />
                </td>
                <td>
                    <SelectInput
                        name={`${key}-column-${index}`}
                        choices={getColumnsOptionsWithNull}
                        multiple={false}
                        handleSelect={value => changeArraySettings(key, index, "column", value)}
                        value={row.column}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-header-${index}`}
                        value={row.header}
                        onChange={e => changeArraySettings(key, index, "header", e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-delimiter-${index}`}
                        className="col-md-12"
                        value={row.delimiter}
                        onChange={e => changeArraySettings(key, index, "delimiter", e.target.value)}
                    />
                </td>
                <td>
                    <SelectInput
                        name={`${key}-on_click_event-${index}`}
                        choices={getInteractivityOptions}
                        multiple={false}
                        handleSelect={value =>
                            changeArraySettings(key, index, "on_click_event", value)
                        }
                        value={row.on_click_event}
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
