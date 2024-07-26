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
                    <tbody>{items.map((row, index) => this.renderRow(row, index))}</tbody>
                </table>
            </div>
        );
    }
    renderRow(row, index) {
        const {expandRow} = this.props.store.subclass;

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
                <MoveRowTd onDelete={() => deleteArrayElement(key, index)} onEdit={() => expandRow(index)} />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const { collapseRow, handleRowSubmit} = this.props.store.subclass;
        return (
        <tr key={index}>
            <form>
                <TextInput
                    name={`${key}-name-${index}`}
                    value={row.name}
                />
                <IntegerInput
                    name={`${key}-width-${index}`}
                    value={row.width}
                />
                <IntegerInput
                    name={`${key}-height-${index}`}
                    value={row.height}
                />
                <IntegerInput
                    name={`${key}-border-width-${index}`}
                    value={row.border_width}
                />
                <IntegerInput
                    name={`${key}-rx-${index}`}
                    value={row.rx}
                />
                <IntegerInput
                    name={`${key}-ry-${index}`}
                    value={row.ry}
                />
                <TextInput
                    name={`${key}-bg-color-${index}`}
                    className="col-md-12"
                    value={row.bg_color}
                />
                <TextInput
                    name={`${key}-border-color-${index}`}
                    className="col-md-12"
                    value={row.border_color}
                />
                <TextInput
                    name={`${key}-font-color-${index}`}
                    className="col-md-12"
                    value={row.font_color}
                />
                <TextInput
                    name={`${key}-text-style-${index}`}
                    className="col-md-12"
                    value={row.text_style}
                />
                <FormActions handleSubmit={e => handleRowSubmit(e.target)} cancel={e => collapseRow(e.target)} />
            </form>
        </tr>
    );
    }
}
PrismaSectionsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaSectionsTable;
