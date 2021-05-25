import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import CheckboxInput from "shared/components/CheckboxInput";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";
import SelectInput from "shared/components/SelectInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import HelpTextPopup from "shared/components/HelpTextPopup";
import SortableList from "shared/components/SortableList";

import {HelpText} from "./common";

const setDefaultItems = function(row) {
    return [
        {id: 1, label: "This is item A", included: true},
        {id: 2, label: "This is item B", included: true},
        {id: 3, label: "This is item C", included: true},
        {id: 4, label: "This is item D", included: true},
    ];
};

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
                changeIncludedArrayItems,
            } = this.props.store.subclass,
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
                            const items = e.target.checked ? setDefaultItems(row) : null;
                            changeArraySettings(key, index, "items", items);
                        }}
                        label="Customize items"
                    />
                    {hasItems ? (
                        <SortableList
                            items={row.items}
                            onOrderChange={(id, oldIndex, newIndex) => {
                                changeOrderArrayItems(key, index, oldIndex, newIndex);
                            }}
                            onSelectChange={(id, checked) => {
                                changeIncludedArrayItems(key, index, id, checked);
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
