import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import TextInput from "shared/components/TextInput";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";

// wip - continue
@observer
class DescriptiveTable extends Component {
    render() {
        const {dp} = this.props,
            store = dp.store.descriptiveTextStore;
        return (
            <>
                <h3>Descriptive text columns</h3>
                <table className="table table-sm table-bordered">
                    <thead>
                        <tr>
                            <th>Column header</th>
                            <th>Display name</th>
                            <th>Header style</th>
                            <th>Text style</th>
                            <th>Maximum width (pixels)</th>
                            <th>On-click</th>
                            <ActionsTh onClickNew={store.createNew} />
                        </tr>
                    </thead>
                    <colgroup>
                        <col width="15%" />
                        <col width="13%" />
                        <col width="13%" />
                        <col width="13%" />
                        <col width="15%" />
                        <col width="15%" />
                        <col width="12%" />
                    </colgroup>
                    <tbody>
                        {_.map(store.settings, (data, idx) => {
                            return (
                                <tr key={idx}>
                                    <td>{/* <SelectInput /> */}</td>
                                    <td>
                                        <TextInput
                                            name={`text-header_name-${idx}`}
                                            onChange={e =>
                                                store.updateElement(
                                                    idx,
                                                    "header_name",
                                                    e.target.value
                                                )
                                            }
                                            required={false}
                                            value={data.header_name}
                                        />
                                    </td>
                                    <td>{/* <SelectInput /> */}</td>
                                    <td>{/* <SelectInput /> */}</td>
                                    <td>
                                        {/* <IntegerInput
                                            name={`text-max_width-${idx}`}
                                            value={data.max_width}
                                            onChange={e =>
                                                store.updateElement(
                                                    idx,
                                                    "max_width",
                                                    e.target.value
                                                )
                                            }
                                        /> */}
                                    </td>
                                    <td>{/* <SelectInput /> */}</td>
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
DescriptiveTable.propTypes = {
    dp: PropTypes.object,
};

export default DescriptiveTable;
