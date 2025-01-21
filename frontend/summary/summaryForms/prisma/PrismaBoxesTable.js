import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import {
    ActionsTh,
    moveArrayElementDown,
    moveArrayElementUp,
    MoveRowTd,
} from "shared/components/EditableRowData";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import wrapRow from "shared/components/WrapRow";

import {PrismaEditableRow} from "./PrismaEditableRow";

const key = "boxes";

@inject("store")
@observer
class PrismaBoxesTable extends Component {
    render() {
        const items = this.props.store.subclass.settings[key],
            {createNewBox} = this.props.store.subclass;

        return (
            <div>
                <h3>Boxes</h3>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="50%" />
                        <col width="35%" />
                        <col width="15%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Section</th>
                            <ActionsTh onClickNew={createNewBox} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((row, index) => {
                            return (
                                <BoxesRow
                                    row={row}
                                    index={index}
                                    key={index}
                                    initiallyEditable={row.label == ""}
                                    editStyles={row.use_style_overrides}
                                />
                            );
                        })}
                    </tbody>
                </table>
            </div>
        );
    }
}

@inject("store")
@observer
class BoxesRow extends PrismaEditableRow {
    renderViewRow(row, index) {
        const {deleteArrayElement, sectionMapping} = this.props.store.subclass;

        return (
            <tr>
                <td>{row.label}</td>
                <td>{sectionMapping[row.section]}</td>
                <MoveRowTd
                    onDelete={() => deleteArrayElement(key, index)}
                    onEdit={() => this.setState({edit: true})}
                    onMoveUp={() =>
                        moveArrayElementUp(this.props.store.subclass.settings[key], index)
                    }
                    onMoveDown={() =>
                        moveArrayElementDown(this.props.store.subclass.settings[key], index)
                    }
                />
            </tr>
        );
    }
    renderEditRow(row, index) {
        const {
                changeArraySettings,
                getSectionOptions,
                getCountFilters,
                getBoxLayouts,
                toggleStyling,
                getCountBlocks,
                getCountStrategies,
            } = this.props.store.subclass,
            isCard = row.box_layout === "card",
            isList = row.box_layout === "list";
        return (
            <tr>
                <td colSpan="100%">
                    <div className="border p-3 pb-3 edit-form-background pad-form">
                        {wrapRow(
                            [
                                <TextInput
                                    key={1}
                                    name={`${key}-name-${index}`}
                                    value={row.label}
                                    label="Name"
                                    onChange={e =>
                                        changeArraySettings(key, index, "label", e.target.value)
                                    }
                                />,
                                <SelectInput
                                    key={2}
                                    name={`${key}-section-${index}`}
                                    value={row.section}
                                    label="Section"
                                    handleSelect={value => {
                                        changeArraySettings(key, index, "section", value);
                                    }}
                                    multiple={false}
                                    choices={getSectionOptions}
                                />,
                                <SelectInput
                                    key={3}
                                    name={`${key}-layout-${index}`}
                                    value={row.box_layout}
                                    label="Layout type for this box"
                                    handleSelect={value =>
                                        changeArraySettings(key, index, "box_layout", value)
                                    }
                                    multiple={false}
                                    choices={getBoxLayouts}
                                />,
                            ],
                            "form-row",
                            "col-md-4"
                        )}
                        <div className="form-row">
                            {isCard ? (
                                <>
                                    <div className="col-md-4">
                                        <SelectInput
                                            name={`${key}-layout-${index}-count_strategy`}
                                            value={row.count_strategy}
                                            label="Reference count strategy"
                                            handleSelect={value =>
                                                changeArraySettings(
                                                    key,
                                                    index,
                                                    "count_strategy",
                                                    value
                                                )
                                            }
                                            multiple={false}
                                            choices={getCountStrategies}
                                        />
                                    </div>
                                    {row.count_strategy == "unique_sum" ? (
                                        <div className="col-md-8">
                                            <SelectInput
                                                name={`${key}-count_filters-${index}`}
                                                value={row.count_filters}
                                                label="Add references related to this tag, search, or import"
                                                handleSelect={value => {
                                                    changeArraySettings(
                                                        key,
                                                        index,
                                                        "count_filters",
                                                        value
                                                    );
                                                }}
                                                multiple={true}
                                                choices={getCountFilters}
                                            />
                                        </div>
                                    ) : null}
                                    {row.count_strategy && row.count_strategy != "unique_sum" ? (
                                        <>
                                            <div className="col-md-4">
                                                <SelectInput
                                                    name={`${key}-count_include-${index}`}
                                                    value={row.count_include}
                                                    label="Included blocks"
                                                    handleSelect={value => {
                                                        changeArraySettings(
                                                            key,
                                                            index,
                                                            "count_include",
                                                            value
                                                        );
                                                    }}
                                                    multiple={true}
                                                    choices={getCountBlocks(row)}
                                                />
                                            </div>
                                            <div className="col-md-4">
                                                <SelectInput
                                                    name={`${key}-count_exclude-${index}`}
                                                    value={row.count_exclude}
                                                    label="Excluded blocks"
                                                    handleSelect={value => {
                                                        changeArraySettings(
                                                            key,
                                                            index,
                                                            "count_exclude",
                                                            value
                                                        );
                                                    }}
                                                    multiple={true}
                                                    choices={getCountBlocks(row)}
                                                />
                                            </div>
                                        </>
                                    ) : null}
                                </>
                            ) : null}
                        </div>
                        {isList ? <ListTable row={row} index={index} /> : null}
                        <div className="form-row">
                            <div className="col-md-4">
                                <CheckboxInput
                                    name={`${key}-toggle-styling-${index}`}
                                    checked={row.use_style_overrides}
                                    label="Override default styling"
                                    onChange={e => {
                                        toggleStyling(key, index, e.target.checked);
                                        this.setState({edit_styles: e.target.checked});
                                    }}
                                />
                            </div>
                        </div>
                        {this.state.edit_styles && this.renderStyleOptions(key, row, index)}
                        <div className="form-row justify-content-center">
                            <button
                                className="btn btn-primary mx-2 py-2"
                                type="button"
                                style={{width: "15rem", padding: "0.7rem"}}
                                onClick={() => this.setState({edit: false})}>
                                Close
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        );
    }
}
PrismaBoxesTable.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class ListTable extends Component {
    render() {
        const {row, index, store} = this.props,
            {
                createNewBoxItem,
                changeSettings,
                getCountFilters,
                deleteArrayElement,
            } = store.subclass,
            items = row.items;

        return (
            <div className="form-row">
                <h4>Bulleted List</h4>
                <table className="table table-sm table-striped">
                    <colgroup>
                        <col width="45%" />
                        <col width="45%" />
                        <col width="10%" />
                    </colgroup>
                    <thead>
                        <tr>
                            <th>Label</th>
                            <th>Selectors</th>
                            <ActionsTh onClickNew={() => createNewBoxItem(index)} />
                        </tr>
                    </thead>
                    <tbody>
                        {items.map((item_row, item_index) => {
                            return (
                                <tr key={item_index}>
                                    <td>
                                        <TextInput
                                            name={`box-${index}-list-${item_index}-label`}
                                            value={item_row.label}
                                            label=""
                                            onChange={e =>
                                                changeSettings(
                                                    `boxes[${index}].items[${item_index}].label`,
                                                    e.target.value
                                                )
                                            }
                                        />
                                    </td>
                                    <td>
                                        <SelectInput
                                            name={`box-${index}-list-${item_index}-count_filters`}
                                            value={item_row.count_filters}
                                            handleSelect={values => {
                                                changeSettings(
                                                    `boxes[${index}].items[${item_index}].count_filters`,
                                                    values
                                                );
                                            }}
                                            multiple={true}
                                            choices={getCountFilters}
                                        />
                                    </td>
                                    <MoveRowTd
                                        onDelete={() =>
                                            deleteArrayElement(`boxes[${index}].items`, item_index)
                                        }
                                    />
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        );
    }
}
ListTable.propTypes = {
    store: PropTypes.object,
    index: PropTypes.number,
    row: PropTypes.object,
};

export default PrismaBoxesTable;
