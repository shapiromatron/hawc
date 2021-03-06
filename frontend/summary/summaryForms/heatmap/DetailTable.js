import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";

const key = "table_fields";

@inject("store")
@observer
class DetailTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewTableRow} = this.props.store.subclass;

        return (
            <table className="table table-sm table-striped">
                <colgroup>
                    <col width="40%" />
                    <col width="25%" />
                    <col width="25%" />
                    <col width="10%" />
                </colgroup>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Delimiter</th>
                        <th>Interactivity</th>
                        <ActionsTh onClickNew={createNewTableRow} />
                    </tr>
                </thead>
                <tbody>{items.map((row, index) => this.renderRow(row, index))}</tbody>
            </table>
        );
    }
    renderRow(row, index) {
        const {
            getColumnsOptionsWithNull,
            getDpeSettings,
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
                        onChange={e =>
                            changeArraySettings(key, index, "delimiter", e.target.value.trim())
                        }
                    />
                </td>
                <td>
                    <SelectInput
                        name={`${key}-on_click_event-${index}`}
                        choices={getDpeSettings}
                        multiple={false}
                        handleSelect={value =>
                            changeArraySettings(key, index, "on_click_event", value)
                        }
                        value={row.on_click_event}
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
DetailTable.propTypes = {
    store: PropTypes.object,
};

export default DetailTable;
