import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import CheckboxInput from "shared/components/CheckboxInput";
import FloatInput from "shared/components/FloatInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

import ValueDisplaySelect from "../../summary/heatmap/ValueDisplaySelect";
import AxisLabelTable from "./AxisLabelTable";
import DetailTable from "./DetailTable";
import FilterTable from "./FilterTable";
import FilterWidgetTable from "./FilterWidgetTable";
import {MissingData, RefreshRequired} from "./common";

@inject("store")
@observer
class VisualCustomizationPanel extends Component {
    render() {
        const {hasDataset, dataRefreshRequired} = this.props.store.base;
        let content;
        if (!hasDataset) {
            content = <MissingData />;
        } else if (dataRefreshRequired) {
            content = <RefreshRequired />;
        } else {
            content = this.renderForm();
        }
        return (
            <div>
                <legend>Visualization customization</legend>
                <p className="form-text text-muted">
                    Customize the look, feel, and layout of the current visual.
                </p>
                {content}
            </div>
        );
    }
    renderForm() {
        const {visualCustomizationPanelActiveTab, changeActiveVisualCustomizationTab} =
            this.props.store.subclass;
        return (
            <Tabs
                selectedIndex={visualCustomizationPanelActiveTab}
                onSelect={changeActiveVisualCustomizationTab}>
                <TabList>
                    <Tab>Heatmap</Tab>
                    <Tab>Data filters</Tab>
                    <Tab>Filter widgets</Tab>
                    <Tab>Data tables</Tab>
                    <Tab>Advanced</Tab>
                </TabList>
                <TabPanel>{this.renderHeatmapTab()}</TabPanel>
                <TabPanel>{this.renderFilterTab()}</TabPanel>
                <TabPanel>{this.renderFilterWidgetTab()}</TabPanel>
                <TabPanel>{this.renderDataTableTab()}</TabPanel>
                <TabPanel>{this.renderAdvancedTab()}</TabPanel>
            </Tabs>
        );
    }
    renderHeatmapTab() {
        const {settings, changeSettings} = this.props.store.subclass;
        return (
            <div>
                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Plot labels</h4>
                        <div className="row">
                            <div className="col-md-4">
                                <TextInput
                                    name="title.text"
                                    label="Title"
                                    value={settings.title.text}
                                    onChange={e => changeSettings(e.target.name, e.target.value)}
                                />
                            </div>
                            <div className="col-md-4">
                                <TextInput
                                    name="x_label.text"
                                    label="X-axis label"
                                    value={settings.x_label.text}
                                    onChange={e => changeSettings(e.target.name, e.target.value)}
                                />
                            </div>
                            <div className="col-md-4">
                                <TextInput
                                    name="y_label.text"
                                    label="Y-axis label"
                                    value={settings.y_label.text}
                                    onChange={e => changeSettings(e.target.name, e.target.value)}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Rows</h4>
                        <AxisLabelTable settingsKey={"y_fields"} />
                    </div>
                </div>

                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Columns</h4>
                        <AxisLabelTable settingsKey={"x_fields"} />
                    </div>
                </div>
            </div>
        );
    }
    renderFilterTab() {
        return (
            <div>
                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Data filters</h4>
                        <p className="text-muted">
                            Determine which rows of your dataset should be displayed. By default all
                            data from a dataset are shown on the heatmp, but filters can be added to
                            only present a subset of the data.
                        </p>
                        <FilterTable />
                    </div>
                </div>
            </div>
        );
    }
    renderFilterWidgetTab() {
        return (
            <div>
                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Filter widgets</h4>
                        <p className="text-muted">
                            A filter widget is shown to the right of a heatmap and allows users to
                            interactively filter content which should be presented in the heatmap
                            and summary table. Filter widgets are optional, but enable users to
                            interactively slice the data in new ways.
                        </p>
                        <FilterWidgetTable />
                    </div>
                </div>
            </div>
        );
    }
    renderDataTableTab() {
        return (
            <div>
                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Data tables</h4>
                        <p className="text-muted">
                            Summary table of selected content below the heatmap. If one or more
                            columns are displayed, then the summary table will be shown.
                        </p>
                        <DetailTable />
                    </div>
                </div>
            </div>
        );
    }
    renderAdvancedTab() {
        const {settings, changeSettings, getColumnsOptionsWithNull} = this.props.store.subclass;
        return (
            <div>
                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Plot</h4>
                        <div className="row">
                            <div className="col-md-3">
                                <FloatInput
                                    name="cell_width"
                                    label="Cell width"
                                    value={settings.cell_width}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-3">
                                <FloatInput
                                    name="cell_height"
                                    label="Cell height"
                                    value={settings.cell_height}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-3">
                                <CheckboxInput
                                    label="Auto-size cells"
                                    name="autosize_cells"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.autosize_cells}
                                    helpText={"Overrides cell dimensions for calculated best fit"}
                                />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-md-3">
                                <FloatInput
                                    name="padding.top"
                                    label="Padding top"
                                    value={settings.padding.top}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-3">
                                <FloatInput
                                    name="padding.left"
                                    label="Padding left"
                                    value={settings.padding.left}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-3">
                                <FloatInput
                                    name="padding.bottom"
                                    label="Padding bottom"
                                    value={settings.padding.bottom}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-3">
                                <FloatInput
                                    name="padding.right"
                                    label="Padding right"
                                    value={settings.padding.right}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-md-3">
                                <TextInput
                                    label="Color range (start)"
                                    name="color_range1"
                                    type="color"
                                    value={settings.color_range[0]}
                                    onChange={e => changeSettings("color_range.0", e.target.value)}
                                />
                            </div>
                            <div className="col-md-3">
                                <TextInput
                                    label="Color range (end)"
                                    name="color_range2"
                                    type="color"
                                    value={settings.color_range[1]}
                                    onChange={e => changeSettings("color_range.1", e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-md-3">
                                <CheckboxInput
                                    label="Compress X fields"
                                    name="compress_x"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.compress_x}
                                    helpText={"Hides columns with no datapoints"}
                                />
                            </div>
                            <div className="col-md-3">
                                <CheckboxInput
                                    label="Compress Y fields"
                                    name="compress_y"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.compress_y}
                                    helpText={"Hides rows with no datapoints"}
                                />
                            </div>
                            <div className="col-md-3">
                                <CheckboxInput
                                    label="Show cell grid"
                                    name="show_grid"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.show_grid}
                                />
                            </div>
                            <div className="col-md-3">
                                <CheckboxInput
                                    label="Show grand totals"
                                    name="show_totals"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.show_totals}
                                />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-md-3">
                                <CheckboxInput
                                    label="Show null field values"
                                    name="show_null"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.show_null}
                                    helpText={"Display data with <null> values in selected axes"}
                                />
                            </div>
                            <div className="col-md-3">
                                <ValueDisplaySelect
                                    onChange={value => changeSettings("show_counts", value)}
                                    value={settings.show_counts}
                                />
                            </div>
                            <div className="col-md-3">
                                <SelectInput
                                    label="Count column"
                                    name={"count_column"}
                                    choices={getColumnsOptionsWithNull}
                                    multiple={false}
                                    handleSelect={value => changeSettings("count_column", value)}
                                    value={settings.count_column}
                                    helpText={
                                        "Column used to calculate heatmap and filter widget counts; defaults to number of rows in the dataset."
                                    }
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Axes</h4>
                        <div className="row">
                            <div className="col-md-3">
                                <FloatInput
                                    name="x_tick_rotate"
                                    label="X-axis tick rotation"
                                    value={settings.x_tick_rotate}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-3">
                                <FloatInput
                                    name="y_tick_rotate"
                                    label="Y-axis tick rotation"
                                    value={settings.y_tick_rotate}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-3">
                                <CheckboxInput
                                    label="Auto-rotate tick labels"
                                    name="autorotate_tick_labels"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.autorotate_tick_labels}
                                    helpText={"Overrides tick rotations with calculated fit"}
                                />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-md-3">
                                <SelectInput
                                    handleSelect={value =>
                                        changeSettings("x_axis_bottom", value == "bottom")
                                    }
                                    choices={[
                                        {id: "top", label: "Top"},
                                        {id: "bottom", label: "Bottom"},
                                    ]}
                                    value={settings.x_axis_bottom ? "bottom" : "top"}
                                    multiple={false}
                                    label="X-axis position"
                                />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-md-3">
                                <CheckboxInput
                                    id="show_axis_border"
                                    label="Show tick border"
                                    name="show_axis_border"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.show_axis_border}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Title</h4>
                        <div className="row">
                            <div className="col-md-4">
                                <FloatInput
                                    name="title.x"
                                    label="X-coordinate"
                                    value={settings.title.x}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-4">
                                <FloatInput
                                    name="title.y"
                                    label="Y-coordinate"
                                    value={settings.title.y}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-4">
                                <FloatInput
                                    name="title.rotate"
                                    label="Rotation"
                                    value={settings.title.rotate}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">X-axis label</h4>
                        <div className="row">
                            <div className="col-md-4">
                                <FloatInput
                                    name="x_label.x"
                                    label="X-coordinate"
                                    value={settings.x_label.x}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-4">
                                <FloatInput
                                    name="x_label.y"
                                    label="Y-coordinate"
                                    value={settings.x_label.y}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-4">
                                <FloatInput
                                    name="x_label.rotate"
                                    label="Rotation"
                                    value={settings.x_label.rotate}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Y-axis label</h4>
                        <div className="row">
                            <div className="col-md-4">
                                <FloatInput
                                    name="y_label.x"
                                    label="X-coordinate"
                                    value={settings.y_label.x}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-4">
                                <FloatInput
                                    name="y_label.y"
                                    label="Y-coordinate"
                                    value={settings.y_label.y}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                            <div className="col-md-4">
                                <FloatInput
                                    name="y_label.rotate"
                                    label="Rotation"
                                    value={settings.y_label.rotate}
                                    onChange={e =>
                                        changeSettings(e.target.name, parseFloat(e.target.value))
                                    }
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="card-body">
                        <h4 className="card-title">Interactivity</h4>
                        <div className="row">
                            <div className="col-md-3">
                                <CheckboxInput
                                    id="hawc_interactivity"
                                    label="HAWC interactivity"
                                    name="hawc_interactivity"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.hawc_interactivity}
                                />
                            </div>
                            <div className="col-md-3">
                                <CheckboxInput
                                    id="show_tooltip"
                                    label="Show tooltips"
                                    name="show_tooltip"
                                    onChange={e => changeSettings(e.target.name, e.target.checked)}
                                    checked={settings.show_tooltip}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
VisualCustomizationPanel.propTypes = {
    store: PropTypes.object,
};
export default VisualCustomizationPanel;
