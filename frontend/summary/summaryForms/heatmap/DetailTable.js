import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

const key = "table_fields";

@inject("store")
@observer
class DetailTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewTableRow} = this.props.store.subclass;

        return (
            <table className="table table-condensed table-striped">
                <colgroup>
                    <col width="50%" />
                    <col width="10%" />
                    <col width="30%" />
                    <col width="10%" />
                </colgroup>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Delimiter</th>
                        <th>Interactivity</th>
                        <th>
                            Actions&nbsp;
                            <button
                                className="btn btn-small btn-primary"
                                title="New row"
                                onClick={createNewTableRow}>
                                <i className="fa fa-plus"></i>
                            </button>
                        </th>
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
                        className="span12"
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
                        className="span12"
                        choices={getDpeSettings}
                        multiple={false}
                        handleSelect={value =>
                            changeArraySettings(key, index, "on_click_event", value)
                        }
                        value={row.on_click_event}
                    />
                </td>
                <td>
                    <button
                        className="btn btn-small btn-default"
                        title="Move row up"
                        onClick={() => moveArrayElementUp(key, index)}>
                        <i className="fa fa-long-arrow-up"></i>
                    </button>
                    <button
                        className="btn btn-small btn-default"
                        title="Move row down"
                        onClick={() => moveArrayElementDown(key, index)}>
                        <i className="fa fa-long-arrow-down"></i>
                    </button>
                    <button
                        className="btn btn-small btn-danger"
                        title="Delete row"
                        onClick={() => deleteArrayElement(key, index)}>
                        <i className="fa fa-trash"></i>
                    </button>
                </td>
            </tr>
        );
    }
}
DetailTable.propTypes = {
    store: PropTypes.object,
};

export default DetailTable;
