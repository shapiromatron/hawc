import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";

import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import {FilterChoices} from "../shared";

const filterChoices = [
    {id: FilterChoices.gt, label: ">"},
    {id: FilterChoices.gte, label: "≥"},
    {id: FilterChoices.lt, label: "<"},
    {id: FilterChoices.lte, label: "≤"},
    {id: FilterChoices.exact, label: "exact"},
    {id: FilterChoices.contains, label: "contains"},
    {id: FilterChoices.not_contains, label: "does not contain"},
];

@observer
class FilterTable extends Component {
    render() {
        const {dp} = this.props,
            store = dp.store.filterStore;
        return (
            <>
                <h3>Row filters</h3>
                <p className="form-text text-muted">
                    Use filters to determine which components of your dataset should be displayed on
                    the figure.
                </p>
                <table className="table table-sm table-bordered">
                    <thead>
                        <tr>
                            <th>Number</th>
                            <th>Field name</th>
                            <th>Filter type</th>
                            <th>Value</th>
                            <ActionsTh onClickNew={store.createNew} />
                        </tr>
                    </thead>
                    <colgroup>
                        <col width="5%" />
                        <col width="30%" />
                        <col width="20%" />
                        <col width="30%" />
                        <col width="15%" />
                    </colgroup>
                    <tbody>
                        {_.map(store.settings, (data, idx) => {
                            return (
                                <tr key={idx}>
                                    <td>{idx + 1}</td>
                                    <td>
                                        <SelectInput
                                            name={`sort-field_name-${idx}`}
                                            handleSelect={value => {
                                                store.updateElement(idx, "field_name", value);
                                            }}
                                            choices={dp._get_header_options_react(true)}
                                            required={false}
                                            value={data.field_name}
                                        />
                                    </td>
                                    <td>
                                        <SelectInput
                                            name={`sort-quantifier-${idx}`}
                                            handleSelect={value =>
                                                store.updateElement(idx, "quantifier", value)
                                            }
                                            choices={filterChoices}
                                            required={false}
                                            value={data.quantifier}
                                        />
                                    </td>
                                    <td>
                                        <TextInput
                                            name={`filter-value-${idx}`}
                                            onChange={e =>
                                                store.updateElement(idx, "value", e.target.value)
                                            }
                                            required={false}
                                            value={data.value}
                                        />
                                    </td>
                                    <MoveRowTd
                                        onMoveUp={() => store.moveUp(idx)}
                                        onMoveDown={() => store.moveDown(idx)}
                                        onDelete={() => store.delete(idx)}
                                    />
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </>
        );
    }
}
FilterTable.propTypes = {
    dp: PropTypes.object,
};

export default (tab, dp) => {
    const div = document.createElement("div");
    ReactDOM.render(<FilterTable dp={dp} />, div);
    tab.append(div);
};
