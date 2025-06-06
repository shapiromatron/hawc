import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {createRoot} from "react-dom/client";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import RadioInput from "shared/components/RadioInput";
import SelectInput from "shared/components/SelectInput";
import SortableList from "shared/components/SortableList";

import {OrderChoices} from "../shared";

@observer
class SortingTable extends Component {
    render() {
        const {dp} = this.props,
            store = dp.store.sortStore;
        return (
            <>
                <h3>Row sorting</h3>
                <p className="form-text text-muted">
                    Sorting determines the order which rows will appear; sorts can be overridden
                    using the manual override table below.
                </p>
                <table className="table table-sm table-bordered">
                    <thead>
                        <tr>
                            <th>Field name</th>
                            <th>Sort order</th>
                            <ActionsTh onClickNew={store.createNew} />
                        </tr>
                    </thead>
                    <colgroup>
                        <col width="40%" />
                        <col width="45%" />
                        <col width="15%" />
                    </colgroup>
                    <tbody>
                        {_.map(store.settings, (data, idx) => {
                            return (
                                <tr key={idx}>
                                    <td>
                                        <SelectInput
                                            name={`sort-field_name-${idx}`}
                                            handleSelect={value => {
                                                store.updateElement(idx, "field_name", value);
                                            }}
                                            choices={store.fieldColumns}
                                            required={false}
                                            value={data.field_name}
                                        />
                                    </td>
                                    <td>
                                        <RadioInput
                                            name={`sort-order-${idx}`}
                                            onChange={value => store.updateOrder(idx, value)}
                                            choices={[
                                                {id: OrderChoices.asc, label: "Ascending"},
                                                {id: OrderChoices.desc, label: "Descending"},
                                                {id: OrderChoices.custom, label: "Custom"},
                                            ]}
                                            required={false}
                                            horizontal={true}
                                            value={data.order}
                                        />
                                        {data.order === OrderChoices.custom ? (
                                            <SortableList
                                                items={data.custom.map(d => {
                                                    return {id: d, label: d};
                                                })}
                                                onOrderChange={(id, oldIndex, newIndex) =>
                                                    store.changeOrder(idx, oldIndex, newIndex)
                                                }
                                            />
                                        ) : null}
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
                <hr />
            </>
        );
    }
}
SortingTable.propTypes = {
    dp: PropTypes.object,
};

export default (tab, dp) => {
    const div = document.createElement("div");
    const root = createRoot(div);
    root.render(<SortingTable dp={dp} />);
    tab.append(div);
};
