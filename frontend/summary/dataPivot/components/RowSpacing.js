import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import ReactDOM from "react-dom";

import CheckboxInput from "shared/components/CheckboxInput";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";

@observer
class RowSpacing extends Component {
    render() {
        const {dp} = this.props,
            store = dp.store.spacerStore;
        return (
            <>
                <h3>Additional row spacing</h3>
                <p className="form-text text-muted">
                    Add additional-space between rows, and optionally a horizontal line.
                </p>
                <table className="table table-sm table-bordered">
                    <thead>
                        <tr>
                            <th>Row index</th>
                            <th>Show line?</th>
                            <th>Line style</th>
                            <th>Extra space?</th>
                            <ActionsTh onClickNew={store.createNew} />
                        </tr>
                    </thead>
                    <colgroup>
                        <col width="20%" />
                        <col width="20%" />
                        <col width="25%" />
                        <col width="20%" />
                        <col width="15%" />
                    </colgroup>
                    <tbody>
                        {_.map(store.settings, (data, idx) => {
                            return (
                                <tr key={idx}>
                                    <td>
                                        <IntegerInput
                                            name={`spacing-index-${idx}`}
                                            value={data.index}
                                            onChange={e =>
                                                store.updateElement(idx, "index", e.target.value)
                                            }
                                        />
                                    </td>
                                    <td>
                                        <CheckboxInput
                                            checked={data.show_line}
                                            onChange={e =>
                                                store.updateElement(
                                                    idx,
                                                    "show_line",
                                                    e.target.checked
                                                )
                                            }
                                        />
                                    </td>
                                    <td>
                                        <SelectInput
                                            name={`sort-line_style-${idx}`}
                                            handleSelect={value => {
                                                store.updateElement(idx, "line_style", value);
                                            }}
                                            choices={store.rootStore.getLineStyleOptions()}
                                            required={false}
                                            value={data.line_style}
                                        />
                                    </td>
                                    <td>
                                        <CheckboxInput
                                            checked={data.extra_space}
                                            onChange={e => {
                                                store.updateElement(
                                                    idx,
                                                    "extra_space",
                                                    e.target.checked
                                                );
                                            }}
                                        />
                                    </td>
                                    <MoveRowTd onDelete={() => store.delete(idx)} />
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
RowSpacing.propTypes = {
    dp: PropTypes.object,
};

export default (tab, dp) => {
    const div = document.createElement("div");
    ReactDOM.render(<RowSpacing dp={dp} />, div);
    tab.append(div);
};
