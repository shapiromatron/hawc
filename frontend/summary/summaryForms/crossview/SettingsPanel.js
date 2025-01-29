import _ from "lodash";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import CheckboxInput from "shared/components/CheckboxInput";
import {ActionsTh, MoveRowTd} from "shared/components/EditableRowData";
import FloatInput from "shared/components/FloatInput";
import IntegerInput from "shared/components/IntegerInput";
import Loading from "shared/components/Loading";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";
import {DATA_FILTER_OPTIONS} from "summary/summary/filters";

import FilterLogic from "../shared/FilterLogic";

const fieldChoiceLabel = (value, choices) => _.find(choices, {id: value}).label;

@inject("store")
@observer
class ArrayTableRow extends Component {
    render() {
        const {store, widths, names, heading, helpText, arrayName, Row} = this.props,
            {settings, createArrayElement} = store.subclass;
        return (
            <div className="row">
                <div className="col">
                    {heading ? <h4>{heading}</h4> : null}
                    <table className="table table-sm table-striped">
                        <colgroup>
                            {widths.map((d, i) => (
                                <col key={i} width={`${d}%`} />
                            ))}
                        </colgroup>
                        <thead>
                            <tr>
                                {names.map((d, i) => (
                                    <th key={i}>{d}</th>
                                ))}
                                <ActionsTh onClickNew={d => createArrayElement(arrayName)} />
                            </tr>
                        </thead>
                        <tbody>
                            {settings[arrayName].map((item, index) => (
                                <Row key={index} index={index} arrayName={arrayName} />
                            ))}
                        </tbody>
                    </table>
                    {helpText ? <p className="text-muted">{helpText}</p> : null}
                </div>
            </div>
        );
    }
}
ArrayTableRow.propTypes = {
    store: PropTypes.object,
    widths: PropTypes.arrayOf(PropTypes.number).isRequired,
    names: PropTypes.arrayOf(PropTypes.string).isRequired,
    heading: PropTypes.string,
    helpText: PropTypes.string,
    arrayName: PropTypes.string.isRequired,
    Row: PropTypes.elementType.isRequired,
};

@inject("store")
@observer
class GeneralSettingsTab extends Component {
    render() {
        const {store} = this.props,
            {changeSetting, settings} = store.subclass;
        return (
            <div className="row">
                <div className="col-4">
                    <IntegerInput
                        name="width"
                        value={settings.width}
                        label="Overall Width (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="Overall width, including plot and tags"
                    />
                </div>
                <div className="col-4">
                    <TextInput
                        name="xAxisLabel"
                        value={settings.xAxisLabel}
                        label="X-axis label"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-4">
                    <TextInput
                        name="yAxisLabel"
                        value={settings.yAxisLabel}
                        label="Y-axis label"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="width"
                        value={settings.width}
                        label="Overall Width (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="Overall width, including plot and tags"
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="height"
                        value={settings.height}
                        label="Overall Height (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="Overall height, including plot and tags"
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="inner_width"
                        value={settings.inner_width}
                        label="Plot Width (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="inner_height"
                        value={settings.inner_height}
                        label="Plot Height (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="padding_left"
                        value={settings.padding_left}
                        label="Plot Padding Left (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="padding_top"
                        value={settings.padding_top}
                        label="Plot Padding Top (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                <div className="col-4">
                    <p className="my-1">&nbsp;</p>
                    <CheckboxInput
                        name="dose_isLog"
                        label="Use Logscale for Dose"
                        onChange={e => changeSetting(e.target.name, e.target.checked)}
                        checked={settings.dose_isLog}
                    />
                </div>
                <div className="col-4">
                    <TextInput
                        name="dose_range"
                        value={settings.dose_range}
                        label="Dose Axis range"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                        helpText='If left blank, calculated automatically from data (ex: "1, 100").'
                    />
                </div>
                <div className="col-4">
                    <TextInput
                        name="response_range"
                        value={settings.response_range}
                        label="Response Axis range"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                        helpText='If left blank, calculated automatically from data (ex: "-0.5, 2.5").'
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="title_x"
                        value={settings.title_x}
                        label="Title x offset (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="x-offset from default location (centered at top of plot)"
                    />
                    <IntegerInput
                        name="title_y"
                        value={settings.title_y}
                        label="Title y offset (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="y-offset from default location (centered at top of plot)"
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="xlabel_x"
                        value={settings.xlabel_x}
                        label="X label x offset (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="x-offset from default location (centered below x-axis)"
                    />
                    <IntegerInput
                        name="xlabel_y"
                        value={settings.xlabel_y}
                        label="X label y offset (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="y-offset from default location (centered below x-axis)"
                    />
                </div>
                <div className="col-4">
                    <IntegerInput
                        name="ylabel_x"
                        value={settings.ylabel_x}
                        label="Y label x offset (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="x-offset from default location (centered left of y-axis)"
                    />
                    <IntegerInput
                        name="ylabel_y"
                        value={settings.ylabel_y}
                        label="Y label y offset (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        helpText="y-offset from default location (centered left of y-axis)"
                    />
                </div>
            </div>
        );
    }
}
GeneralSettingsTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class CrossviewFilterRow extends Component {
    render() {
        const {store, index, arrayName} = this.props,
            {
                changeSetting,
                moveArrayElementUp,
                moveArrayElementDown,
                deleteArrayElement,
                settings,
                fieldChoices,
                fieldOptionChoices,
            } = store.subclass,
            item = settings[arrayName][index];
        return (
            <tr>
                <td>
                    <SelectInput
                        choices={fieldChoices}
                        value={item.name}
                        handleSelect={value => {
                            changeSetting(`${arrayName}[${index}].name`, value);
                            changeSetting(
                                `${arrayName}[${index}].headerName`,
                                fieldChoiceLabel(value, fieldChoices)
                            );
                        }}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].headerName`}
                        value={item.headerName}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <td>
                    <CheckboxInput
                        name={`${arrayName}[${index}].allValues`}
                        label="Show All Values"
                        onChange={e => changeSetting(e.target.name, e.target.checked)}
                        checked={item.allValues}
                    />
                    {item.allValues ? null : (
                        <SelectInput
                            choices={fieldOptionChoices[item.name]}
                            value={item.values}
                            handleSelect={values => {
                                changeSetting(`${arrayName}[${index}].values`, values);
                            }}
                            multiple={true}
                            selectSize={10}
                        />
                    )}
                </td>
                <td>
                    <IntegerInput
                        name={`${arrayName}[${index}].column`}
                        value={item.column}
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${arrayName}[${index}].x`}
                        value={item.x}
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${arrayName}[${index}].y`}
                        value={item.y}
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </td>
                <MoveRowTd
                    onMoveUp={() => moveArrayElementUp(arrayName, index)}
                    onMoveDown={() => moveArrayElementDown(arrayName, index)}
                    onDelete={() => deleteArrayElement(arrayName, index)}
                />
            </tr>
        );
    }
}
CrossviewFilterRow.propTypes = {
    store: PropTypes.object,
    index: PropTypes.number.isRequired,
    arrayName: PropTypes.string.isRequired,
};

@inject("store")
@observer
class CrossviewFilterTab extends Component {
    render() {
        return (
            <ArrayTableRow
                widths={[15, 20, 20, 10, 10, 10, 15]}
                names={[
                    "Field Name",
                    "Header Name",
                    "Values",
                    "Number of Columns",
                    "X position",
                    "Y position",
                ]}
                helpText="Crossview filters are displayed as text on the chart, which is highlighted when a relevant endpoint is selected."
                arrayName="filters"
                Row={CrossviewFilterRow}
            />
        );
    }
}
CrossviewFilterTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class ReferenceLineRow extends Component {
    render() {
        const {store, index, arrayName} = this.props,
            {
                changeSetting,
                moveArrayElementUp,
                moveArrayElementDown,
                deleteArrayElement,
                settings,
            } = store.subclass,
            item = settings[arrayName][index];
        return (
            <tr>
                <td>
                    <FloatInput
                        name={`${arrayName}[${index}].value`}
                        value={item.value}
                        onChange={e => changeSetting(e.target.name, parseFloat(e.target.value))}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].title`}
                        value={item.title}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].style`}
                        value={item.style}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <MoveRowTd
                    onMoveUp={() => moveArrayElementUp(arrayName, index)}
                    onMoveDown={() => moveArrayElementDown(arrayName, index)}
                    onDelete={() => deleteArrayElement(arrayName, index)}
                />
            </tr>
        );
    }
}
ReferenceLineRow.propTypes = {
    store: PropTypes.object,
    index: PropTypes.number.isRequired,
    arrayName: PropTypes.string.isRequired,
};

@inject("store")
@observer
class ReferenceRangeRow extends Component {
    render() {
        const {store, index, arrayName} = this.props,
            {
                changeSetting,
                moveArrayElementUp,
                moveArrayElementDown,
                deleteArrayElement,
                settings,
            } = store.subclass,
            item = settings[arrayName][index];
        return (
            <tr>
                <td>
                    <FloatInput
                        name={`${arrayName}[${index}].lower`}
                        value={item.lower}
                        onChange={e => changeSetting(e.target.name, parseFloat(e.target.lower))}
                    />
                </td>
                <td>
                    <FloatInput
                        name={`${arrayName}[${index}].upper`}
                        value={item.upper}
                        onChange={e => changeSetting(e.target.name, parseFloat(e.target.upper))}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].title`}
                        value={item.title}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].style`}
                        value={item.style}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <MoveRowTd
                    onMoveUp={() => moveArrayElementUp(arrayName, index)}
                    onMoveDown={() => moveArrayElementDown(arrayName, index)}
                    onDelete={() => deleteArrayElement(arrayName, index)}
                />
            </tr>
        );
    }
}
ReferenceRangeRow.propTypes = {
    store: PropTypes.object,
    index: PropTypes.number.isRequired,
    arrayName: PropTypes.string.isRequired,
};

@inject("store")
@observer
class CaptionRow extends Component {
    render() {
        const {store, index, arrayName} = this.props,
            {
                changeSetting,
                moveArrayElementUp,
                moveArrayElementDown,
                deleteArrayElement,
                settings,
            } = store.subclass,
            item = settings[arrayName][index];
        return (
            <tr>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].caption`}
                        value={item.caption}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].style`}
                        value={item.style}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${arrayName}[${index}].max_width`}
                        value={item.max_width}
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${arrayName}[${index}].x`}
                        value={item.x}
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </td>
                <td>
                    <IntegerInput
                        name={`${arrayName}[${index}].y`}
                        value={item.y}
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </td>
                <MoveRowTd
                    onMoveUp={() => moveArrayElementUp(arrayName, index)}
                    onMoveDown={() => moveArrayElementDown(arrayName, index)}
                    onDelete={() => deleteArrayElement(arrayName, index)}
                />
            </tr>
        );
    }
}
CaptionRow.propTypes = {
    store: PropTypes.object,
    index: PropTypes.number.isRequired,
    arrayName: PropTypes.string.isRequired,
};

@inject("store")
@observer
class ReferencesTab extends Component {
    render() {
        return (
            <>
                <ArrayTableRow
                    widths={[20, 40, 20, 20]}
                    names={["Line Value", "Caption", "Style"]}
                    heading="Dose Reference Line"
                    arrayName="reflines_dose"
                    Row={ReferenceLineRow}
                />
                <ArrayTableRow
                    widths={[10, 10, 40, 20, 20]}
                    names={["Lower Value", "Upper Value", "Caption", "Style"]}
                    heading="Dose Reference Range"
                    arrayName="refranges_dose"
                    Row={ReferenceRangeRow}
                />
                <ArrayTableRow
                    widths={[20, 40, 20, 20]}
                    names={["Line Value", "Caption", "Style"]}
                    heading="Response Reference Line"
                    arrayName="reflines_response"
                    Row={ReferenceLineRow}
                />
                <ArrayTableRow
                    widths={[10, 10, 40, 20, 20]}
                    names={["Lower Value", "Upper Value", "Caption", "Style"]}
                    heading="Response Reference Range"
                    arrayName="refranges_response"
                    Row={ReferenceRangeRow}
                />
                <ArrayTableRow
                    widths={[40, 15, 10, 10, 10, 15]}
                    names={["Caption", "Style", "Max Width (px)", "X", "Y"]}
                    heading="Figure Captions"
                    arrayName="labels"
                    Row={CaptionRow}
                />
            </>
        );
    }
}
ReferencesTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class StyleRow extends Component {
    render() {
        const {store, index, arrayName} = this.props,
            {
                changeSetting,
                moveArrayElementUp,
                moveArrayElementDown,
                deleteArrayElement,
                settings,
                fieldChoices,
                fieldOptionChoices,
            } = store.subclass,
            item = settings[arrayName][index];
        return (
            <tr>
                <td>
                    <SelectInput
                        choices={fieldChoices}
                        value={item.field}
                        handleSelect={value => {
                            const firstValue = fieldOptionChoices[value][0].id;
                            changeSetting(`${arrayName}[${index}].headerName`, firstValue);
                            changeSetting(`${arrayName}[${index}].value`, firstValue);
                            changeSetting(`${arrayName}[${index}].field`, value);
                        }}
                    />
                </td>
                <td>
                    <SelectInput
                        choices={fieldOptionChoices[item.field]}
                        value={item.value}
                        handleSelect={value => {
                            changeSetting(`${arrayName}[${index}].value`, value);
                            changeSetting(`${arrayName}[${index}].headerName`, value);
                        }}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].headerName`}
                        value={item.headerName}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].color`}
                        value={item.color}
                        type="color"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <MoveRowTd
                    onMoveUp={() => moveArrayElementUp(arrayName, index)}
                    onMoveDown={() => moveArrayElementDown(arrayName, index)}
                    onDelete={() => deleteArrayElement(arrayName, index)}
                />
            </tr>
        );
    }
}
StyleRow.propTypes = {
    store: PropTypes.object,
    index: PropTypes.number.isRequired,
    arrayName: PropTypes.string.isRequired,
};

@inject("store")
@observer
class StylesTab extends Component {
    render() {
        const {store} = this.props,
            {changeSetting, settings} = store.subclass;
        return (
            <>
                <div className="row">
                    <div className="col-md-4">
                        <TextInput
                            label="Base path color"
                            name="colorBase"
                            type="color"
                            value={settings.colorBase}
                            onChange={e => changeSetting(e.target.name, e.target.value)}
                        />
                    </div>
                    <div className="col-md-4">
                        <TextInput
                            label="Hover path color"
                            name="colorHover"
                            type="color"
                            value={settings.colorHover}
                            onChange={e => changeSetting(e.target.name, e.target.value)}
                        />
                    </div>
                    <div className="col-md-4">
                        <TextInput
                            label="Selected path color"
                            name="colorSelected"
                            type="color"
                            value={settings.colorSelected}
                            onChange={e => changeSetting(e.target.name, e.target.value)}
                        />
                    </div>
                </div>
                <ArrayTableRow
                    widths={[23, 23, 22, 22, 10]}
                    names={["Field Name", "Field Value", "Legend Name", "Color"]}
                    heading="Color Filters"
                    helpText="Custom colors can be applied to paths; these colors are applied based on selectors added below. The first-row is applied last; so if two rules match the same path, the upper-row color will be applied."
                    arrayName="colorFilters"
                    Row={StyleRow}
                />
                <div className="row">
                    <div className="col-md-4">
                        <CheckboxInput
                            name={"colorFilterLegend"}
                            label="Show Color Filter Legend"
                            onChange={e => changeSetting(e.target.name, e.target.checked)}
                            checked={settings.colorFilterLegend}
                        />
                    </div>
                    <div className="col-md-4">
                        <TextInput
                            label="Color Filter Legend Title"
                            name="colorFilterLegendLabel"
                            value={settings.colorFilterLegendLabel}
                            onChange={e => changeSetting(e.target.name, e.target.value)}
                        />
                    </div>
                    <div className="col-md-4">
                        <IntegerInput
                            name="colorFilterLegendX"
                            label="Color Filter Legend X Position"
                            value={settings.colorFilterLegendX}
                            onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        />
                        <IntegerInput
                            name="colorFilterLegendY"
                            label="Color Filter Legend Y Position"
                            value={settings.colorFilterLegendY}
                            onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                        />
                    </div>
                </div>
            </>
        );
    }
}
StylesTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class FilterRow extends Component {
    render() {
        const {store, index, arrayName} = this.props,
            {
                changeSetting,
                moveArrayElementUp,
                moveArrayElementDown,
                deleteArrayElement,
                settings,
                fieldChoices,
            } = store.subclass,
            item = settings[arrayName][index];
        return (
            <tr>
                <td>
                    <SelectInput
                        choices={fieldChoices}
                        value={item.field}
                        handleSelect={value => {
                            changeSetting(`${arrayName}[${index}].field`, value);
                        }}
                    />
                </td>
                <td>
                    <SelectInput
                        choices={DATA_FILTER_OPTIONS}
                        value={item.filterType}
                        handleSelect={value => {
                            changeSetting(`${arrayName}[${index}].filterType`, value);
                        }}
                    />
                </td>
                <td>
                    <TextInput
                        name={`${arrayName}[${index}].value`}
                        value={item.value}
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </td>
                <MoveRowTd
                    onMoveUp={() => moveArrayElementUp(arrayName, index)}
                    onMoveDown={() => moveArrayElementDown(arrayName, index)}
                    onDelete={() => deleteArrayElement(arrayName, index)}
                />
            </tr>
        );
    }
}
FilterRow.propTypes = {
    store: PropTypes.object,
    index: PropTypes.number.isRequired,
    arrayName: PropTypes.string.isRequired,
};

@inject("store")
@observer
class FiltersTab extends Component {
    render() {
        const {store} = this.props,
            {changeSetting, settings} = store.subclass;
        return (
            <>
                <ArrayTableRow
                    widths={[25, 25, 38, 12]}
                    names={["Field Name", "Filter Type", "Value"]}
                    helpText="Filters used to determine which dose-response datasets should be included; by default all plottable datasets are included."
                    arrayName="endpointFilters"
                    Row={FilterRow}
                />
                <div className="row">
                    <div className="col">
                        <FilterLogic
                            filtersLogic={settings.endpointFilterLogic}
                            filtersQuery={settings.filtersQuery}
                            filtersQueryReadable={"TODO"}
                            onLogicChange={v => changeSetting("endpointFilterLogic", v)}
                            onQueryChange={e => changeSetting("filtersQuery", e.target.value)}
                        />
                    </div>
                </div>
            </>
        );
    }
}
FiltersTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class SettingsPanel extends Component {
    componentDidMount() {
        const store = this.props.store.subclass;
        store.checkDataHash();
    }
    componentDidUpdate() {
        const store = this.props.store.subclass;
        store.checkDataHash();
    }
    render() {
        const {activeTab, changeActiveTab, formData} = this.props.store.subclass;
        if (!formData) {
            return (
                <>
                    {<Loading />}
                    <p className="text-muted">Data loading, please wait...</p>
                </>
            );
        }
        return (
            <Tabs selectedIndex={activeTab} onSelect={changeActiveTab}>
                <TabList>
                    <Tab>General Settings</Tab>
                    <Tab>Crossview Filters</Tab>
                    <Tab>References</Tab>
                    <Tab>Styles</Tab>
                    <Tab>Endpoint Filters</Tab>
                </TabList>
                <TabPanel>
                    <GeneralSettingsTab />
                </TabPanel>
                <TabPanel>
                    <CrossviewFilterTab />
                </TabPanel>
                <TabPanel>
                    <ReferencesTab />
                </TabPanel>
                <TabPanel>
                    <StylesTab />
                </TabPanel>
                <TabPanel>
                    <FiltersTab />
                </TabPanel>
            </Tabs>
        );
    }
}
SettingsPanel.propTypes = {
    store: PropTypes.object,
};
export default SettingsPanel;
