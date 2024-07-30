import { inject, observer } from "mobx-react";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { ActionsTh, MoveRowTd } from "shared/components/EditableRowData";
import IntegerInput from "shared/components/IntegerInput";
import TextInput from "shared/components/TextInput";

const key = "sections";

@inject("store")
@observer
class PrismaSectionsTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            { createNewSection } = this.props.store.subclass;
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
                        {items.map((row, index) => { return (<SectionsRow row={row} index={index} />) })}
                    </tbody>
                </table>
            </div>
        );
    }
}

@inject("store")
@observer
class SectionsRow extends Component {
    constructor(props) {
        super(props);
        this.state = { edit: false };
    }
    render() {
        if (this.state.edit) {
            return this.renderEditRow(this.props.row, this.props.index)
        } else {
            return this.renderViewRow(this.props.row, this.props.index)
        }
    }
    renderViewRow(row, index) {
        const { deleteArrayElement } = this.props.store.subclass;

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
                <MoveRowTd onDelete={() => deleteArrayElement(key, index)} onMoveUp={() => this.setState({ edit: true })} />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const { changeArraySettings } = this.props.store.subclass;
        return (
            <tr key={index}>
                <td colSpan="100%">
                    <div className="border my-2 p-2 pb-5 edit-form-background form-row">
                        <TextInput
                            name={`${key}-name-${index}`}
                            className="col-md-4"
                            value={row.name}
                            label="Name"
                            onChange={e => changeArraySettings(key, index, "name", e.target.value)}
                        />
                        <IntegerInput
                            name={`${key}-width-${index}`}
                            className="col-md-4"
                            onChange={e => changeArraySettings(key, index, "column", e.target.value)}
                            label="Width"
                            value={row.width}
                        />
                        <IntegerInput
                            name={`${key}-height-${index}`}
                            className="col-md-4"
                            value={row.height}
                            label="Height"
                            onChange={e => changeArraySettings(key, index, "header", e.target.value)}
                        />
                        <IntegerInput
                            name={`${key}-border-width-${index}`}
                            className="col-md-4"
                            value={row.border_width}
                            label="Border Width"
                            onChange={e =>
                                changeArraySettings(key, index, "border_width", e.target.value)
                            }
                        />
                        <IntegerInput
                            name={`${key}-rx-${index}`}
                            className="col-md-4"
                            value={row.rx}
                            label="rx"
                            onChange={e => changeArraySettings(key, index, "rx", e.target.value)}
                        />
                        <IntegerInput
                            name={`${key}-ry-${index}`}
                            className="col-md-4"
                            value={row.ry}
                            label="ry"
                            onChange={e => changeArraySettings(key, index, "ry", e.target.value)}
                        />
                        <TextInput
                            name={`${key}-bg-color-${index}`}
                            className="col-md-4"
                            value={row.bg_color}
                            label="Background Color"
                            onChange={e => changeArraySettings(key, index, "bg_color", e.target.value)}
                        />
                        <TextInput
                            name={`${key}-border-color-${index}`}
                            className="col-md-4"
                            value={row.border_color}
                            label="Border Color"
                            onChange={e =>
                                changeArraySettings(key, index, "border_color", e.target.value)
                            }
                        />
                        <TextInput
                            name={`${key}-font-color-${index}`}
                            className="col-md-4"
                            value={row.font_color}
                            label="Font Color"
                            onChange={e =>
                                changeArraySettings(key, index, "font_color", e.target.value)
                            }
                        />
                        <TextInput
                            name={`${key}-text-style-${index}`}
                            className="col-md-4"
                            value={row.text_style}
                            label="Text Formatting Style"
                            onChange={e =>
                                changeArraySettings(key, index, "text_style", e.target.value)
                            }
                        />
                        <button
                            className="btn btn-primary"
                            type="button"
                            onClick={() => this.setState({ edit: false })}>
                            Close
                        </button>
                    </div>
                </td>
            </tr>
        );
    }
}
PrismaSectionsTable.propTypes = {
    store: PropTypes.object,
};

export default PrismaSectionsTable;
