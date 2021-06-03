import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";
import SelectInput from "shared/components/SelectInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import HelpTextPopup from "shared/components/HelpTextPopup";

import {HelpText} from "./common";

@inject("store")
@observer
class AxisLabelTable extends Component {
    render() {
        const key = this.props.settingsKey,
            items = this.props.store.subclass.settings[key],
            {createNewAxisLabel} = this.props.store.subclass;

        return (
            <table className="table table-sm table-striped">
                <colgroup>
                    <col width="50%" />
                    <col width="20%" />
                    <col width="20%" />
                    <col width="10%" />
                </colgroup>
                <thead>
                    <tr>
                        <th>Data column</th>
                        <th>
                            Delimiter
                            <HelpTextPopup content={HelpText.delimiter} />
                        </th>
                        <th>
                            Wrap text
                            <HelpTextPopup content={HelpText.wrapText} />
                        </th>
                        <ActionsTh onClickNew={() => createNewAxisLabel(key)} />
                    </tr>
                </thead>
                <tbody>{items.map((row, index) => this.renderRow(row, index))}</tbody>
            </table>
        );
    }
    renderRow(row, index) {
        const key = this.props.settingsKey,
            {
                getColumnsOptionsWithNull,
                changeArraySettings,
                moveArrayElementUp,
                moveArrayElementDown,
                deleteArrayElement,
            } = this.props.store.subclass;

        return (
            <tr key={index}>
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
                        name={`${key}-delimiter-${index}`}
                        value={row.delimiter}
                        onChange={e => changeArraySettings(key, index, "delimiter", e.target.value)}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${key}-wrap_text-${index}`}
                        value={row.wrap_text}
                        onChange={e =>
                            changeArraySettings(
                                key,
                                index,
                                "wrap_text",
                                parseInt(e.target.value) || 0
                            )
                        }
                    />
                </td>
                <MoveRowTd
                    onMoveUp={() => moveArrayElementUp(key, index)}
                    onMoveDown={() => moveArrayElementDown(key, index)}
                    onDelete={() => deleteArrayElement(key, index)}
                />
            </tr>
        );
    }
}
AxisLabelTable.propTypes = {
    store: PropTypes.object,
    settingsKey: PropTypes.string.isRequired,
};

export default AxisLabelTable;
