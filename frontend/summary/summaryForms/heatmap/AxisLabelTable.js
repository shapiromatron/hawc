import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import HelpTextPopup from "shared/components/HelpTextPopup";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import SortableList from "shared/components/SortableList";
import TextInput from "shared/components/TextInput";

import {getColumnValues} from "../../summary/heatmap/common";
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
                    <col width="25%" />
                    <col width="35%" />
                    <col width="15%" />
                    <col width="15%" />
                    <col width="10%" />
                </colgroup>
                <thead>
                    <tr>
                        <th>Data column</th>
                        <th>
                            Custom item ordering
                            <HelpTextPopup content={HelpText.customItems} />
                        </th>
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
                changeOrderArrayItems,
            } = this.props.store.subclass,
            {dataset} = this.props.store.base,
            hasItems = _.isArray(row.items);

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
                    <CheckboxInput
                        checked={hasItems}
                        onChange={e => {
                            const items = e.target.checked
                                ? getColumnValues(dataset, row.column, row.delimiter)
                                : null;
                            changeArraySettings(key, index, "items", items);
                        }}
                        label="Customize items"
                    />
                    {hasItems ? (
                        <SortableList
                            items={row.items}
                            onOrderChange={(_id, oldIndex, newIndex) => {
                                changeOrderArrayItems(key, index, oldIndex, newIndex);
                            }}
                        />
                    ) : null}
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
