import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";
import FormActions from "shared/components/FormActions";

const key = "sections";

@inject("store")
@observer
class PrismaSectionsTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewSection} = this.props.store.subclass;

        return (
            <div>
                <h3>Sections</h3>
                <table className="table table-sm table-striped">
                    {/* <colgroup>
                    <col width="25%" />
                    <col width="25%" />
                    <col width="20%" />
                    <col width="20%" />
                    <col width="10%" />
                </colgroup> */}
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Width</th>
                            <th>Height</th>
                            <th>Border Width</th>
                            <th>rx</th>
                            <th>ry</th>
                            <th>Background Color</th>
                            <th>Border Color</th>
                            <th>Font Color</th>
                            <th>Text Formatting Style</th>
                            <ActionsTh onClickNew={createNewSection} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((row, index) => this.renderRow(row, index))}
                    </tbody>
                </table>
            </div>
        );
    }
    renderRow(row, index) {
        const expandedRow = this.props.store.subclass.settings.expanded_row;
        if (expandedRow.key == key && expandedRow.index == index) {
            return this.renderEditRow(row, index)
        } else {
            return this.renderViewRow(row, index)
        }
    }
    renderViewRow(row, index) {
        const {expandRow, deleteArrayElement} = this.props.store.subclass;

        return (
            <tr key={index}>
                <td>{row.name}</td>
                <td>{row.width}</td>
                <td>{row.height}</td>
                <td>{row.border_width}</td>
                <td>{row.rx}</td>
                <td>{row.ry}</td>
                <td>{row.bg_color}</td>
                <td>{row.border_color}</td>
                <td>{row.font_color}</td>
                <td>{row.text_style}</td>
                <MoveRowTd onDelete={() => deleteArrayElement(key, index)} onMoveUp={() => expandRow(key, index)} />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const { collapseRow, changeArraySettings} = this.props.store.subclass;
        return (
            <div key={index}>
                <TextInput
                    name={`${key}-name-${index}`}
                    value={row.name}
                    onChange={e => changeArraySettings(key, index, "name", e.target.value)}
                />
                <IntegerInput
                    name={`${key}-width-${index}`}
                    onChange={e => changeArraySettings(key, index, "column", e.target.value)}
                    value={row.width}
                />
                <IntegerInput
                    name={`${key}-height-${index}`}
                    value={row.height}
                    onChange={e => changeArraySettings(key, index, "header", e.target.value)}
                />
                <IntegerInput
                    name={`${key}-border-width-${index}`}
                    value={row.border_width}
                    onChange={e =>
                        changeArraySettings(key, index, "border_width", e.target.value)
                    }
                />
                <IntegerInput
                    name={`${key}-rx-${index}`}
                    value={row.rx}
                    onChange={e => changeArraySettings(key, index, "rx", e.target.value)}
                />
                <IntegerInput
                    name={`${key}-ry-${index}`}
                    value={row.ry}
                    onChange={e => changeArraySettings(key, index, "ry", e.target.value)}
                />
                <TextInput
                    name={`${key}-bg-color-${index}`}
                    className="col-md-12"
                    value={row.bg_color}
                    onChange={e => changeArraySettings(key, index, "bg_color", e.target.value)}
                />
                <TextInput
                    name={`${key}-border-color-${index}`}
                    className="col-md-12"
                    value={row.border_color}
                    onChange={e =>
                        changeArraySettings(key, index, "border_color", e.target.value)
                    }
                />
                <TextInput
                    name={`${key}-font-color-${index}`}
                    className="col-md-12"
                    value={row.font_color}
                    onChange={e =>
                        changeArraySettings(key, index, "font_color", e.target.value)
                    }
                />
                <TextInput
                    name={`${key}-text-style-${index}`}
                    className="col-md-12"
                    value={row.text_style}
                    onChange={e =>
                        changeArraySettings(key, index, "text_style", e.target.value)
                    }
                />
                <button
                    className="btn btn-primary"
                    type="button"
                    onClick={collapseRow}>
                    Close
                </button>
            </div>
    );
    }
}
PrismaSectionsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaSectionsTable;
