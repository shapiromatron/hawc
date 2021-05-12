import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import TextInput from "shared/components/TextInput";
import SelectInput from "shared/components/SelectInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import HelpTextPopup from "shared/components/HelpTextPopup";

import {HelpText} from "./common";

const key = "filter_widgets";

@inject("store")
@observer
class FilterWidgetTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewFilterWidget} = this.props.store.subclass;

        return (
            <table className="table table-sm table-striped">
                <colgroup>
                    <col width="25%" />
                    <col width="25%" />
                    <col width="20%" />
                    <col width="20%" />
                    <col width="10%" />
                </colgroup>
                <thead>
                    <tr>
                        <th>Data column</th>
                        <th>
                            Header name
                            <HelpTextPopup content={HelpText.header} />
                        </th>
                        <th>
                            Delimiter
                            <HelpTextPopup content={HelpText.delimiter} />
                        </th>
                        <th>Interactivity</th>
                        <ActionsTh onClickNew={createNewFilterWidget} />
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
            getDpeSettings,
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
                        name={`${key}-header-${index}`}
                        value={row.header}
                        onChange={e =>
                            changeArraySettings(key, index, "header", e.target.value.trim())
                        }
                    />
                </td>
                <td>
                    <TextInput
                        name={`${key}-delimiter-${index}`}
                        className="col-md-12"
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
FilterWidgetTable.propTypes = {
    store: PropTypes.object,
};

export default FilterWidgetTable;
