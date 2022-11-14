import _ from "lodash";
import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import IntegerInput from "shared/components/IntegerInput";
import h from "shared/utils/helpers";

@observer
class ColWidthTable extends Component {
    render() {
        const {totalColumns, updateColWidth, getNormalizedWeights} = this.props.store,
            {column_widths} = this.props.store.settings;
        return (
            <div className="well">
                <h5>Column widths</h5>
                <table className="table table-bordered">
                    <thead>
                        <tr>
                            {_.range(totalColumns).map(col => {
                                return <th key={col}>Column {h.excelColumn(col)}</th>;
                            })}
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            {_.range(totalColumns).map(col => {
                                return (
                                    <td key={col}>
                                        <IntegerInput
                                            minimum={1}
                                            maximum={20}
                                            name="colWidth"
                                            onChange={e =>
                                                updateColWidth(col, parseInt(e.target.value))
                                            }
                                            onInput={e =>
                                                updateColWidth(col, parseInt(e.target.value))
                                            }
                                            value={column_widths[col]}
                                            slider={true}
                                        />
                                    </td>
                                );
                            })}
                        </tr>
                        <tr>
                            {_.map(getNormalizedWeights).map((col, index) => {
                                return <th key={index}>{col}%</th>;
                            })}
                        </tr>
                    </tbody>
                </table>
            </div>
        );
    }
}

ColWidthTable.propTypes = {
    store: PropTypes.object.isRequired,
};

export default ColWidthTable;
