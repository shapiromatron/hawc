import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";
import SelectInput from "shared/components/SelectInput";

@inject("store")
@observer
class AxisLabelTable extends Component {
    render() {
        const key = this.props.settingsKey,
            items = this.props.store.subclass.settings[key],
            {createNewAxisLabel} = this.props.store.subclass;

        return (
            <table className="table table-condensed table-striped">
                <colgroup>
                    <col width="50%" />
                    <col width="20%" />
                    <col width="20%" />
                    <col width="10%" />
                </colgroup>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Delimiter</th>
                        <th>Wrap text</th>
                        <th>
                            Actions&nbsp;
                            <button
                                className="btn btn-sm btn-primary"
                                title="New row"
                                onClick={() => createNewAxisLabel(key)}>
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
                        className="col-md-12"
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
                <td>
                    <button
                        className="btn btn-sm btn-default"
                        title="Move row up"
                        onClick={() => moveArrayElementUp(key, index)}>
                        <i className="fa fa-long-arrow-up"></i>
                    </button>
                    <button
                        className="btn btn-sm btn-default"
                        title="Move row down"
                        onClick={() => moveArrayElementDown(key, index)}>
                        <i className="fa fa-long-arrow-down"></i>
                    </button>
                    <button
                        className="btn btn-sm btn-danger"
                        title="Delete row"
                        onClick={() => deleteArrayElement(key, index)}>
                        <i className="fa fa-trash"></i>
                    </button>
                </td>
            </tr>
        );
    }
}
AxisLabelTable.propTypes = {
    store: PropTypes.object,
    settingsKey: PropTypes.string.isRequired,
};

export default AxisLabelTable;
