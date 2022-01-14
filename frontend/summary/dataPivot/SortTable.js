import _ from "lodash";
import {action, observable} from "mobx";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";

import {
    ActionsTh,
    MoveRowTd,
    moveArrayElementUp,
    moveArrayElementDown,
    deleteArrayElement,
} from "shared/components/EditableRowData";
import RadioInput from "shared/components/RadioInput";
import SelectInput from "shared/components/SelectInput";
import {NULL_CASE} from "./shared";

class SortStore {
    @observable settings = null;
    constructor(settings) {
        this.settings = settings;
    }
    @action.bound createNew() {
        this.settings.push({
            field_name: NULL_CASE,
            ascending: true,
        });
    }
    @action.bound moveUp(idx) {
        moveArrayElementUp(this.settings, idx);
    }
    @action.bound moveDown(idx) {
        moveArrayElementDown(this.settings, idx);
    }
    @action.bound delete(idx) {
        deleteArrayElement(this.settings, idx);
    }
    @action.bound updateElement(idx, field, value) {
        this.settings[idx][field] = value;
    }
}

@observer
class SortingTable extends Component {
    constructor(props) {
        super(props);
        this.store = new SortStore(props.dp.settings.sorts);
    }
    render() {
        const {dp} = this.props,
            {store} = this;

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
                        <col width="40%" />
                        <col width="20%" />
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
                                            choices={dp._get_header_options_react(true)}
                                            required={false}
                                            value={data.field_name}
                                        />
                                    </td>
                                    <td>
                                        <RadioInput
                                            name={`sort-ascending-${idx}`}
                                            onChange={value => {
                                                store.updateElement(idx, "ascending", value);
                                            }}
                                            choices={[
                                                {id: true, label: "Ascending"},
                                                {id: false, label: "Descending"},
                                                {id: "custom", label: "Custom"},
                                            ]}
                                            required={false}
                                            horizontal={true}
                                            value={data.ascending}
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
                <hr />
            </>
        );
    }
}
SortingTable.propTypes = {
    dp: PropTypes.object,
};

const buildSortingTable = (tab, dp) => {
    const div = document.createElement("div");
    ReactDOM.render(<SortingTable dp={dp} />, div);
    tab.append(div);
};
export default buildSortingTable;
