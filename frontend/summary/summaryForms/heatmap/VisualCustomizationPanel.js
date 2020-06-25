import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";

import CheckboxInput from "shared/components/CheckboxInput";
import TextInput from "shared/components/TextInput";
import SelectInput from "shared/components/SelectInput";

import FloatInput from "shared/components/FloatInput";

import {MissingData, RefreshRequired} from "./common";
import AxisLabelTable from "./AxisLabelTable";
import FilterWidgetTable from "./FilterWidgetTable";
import DetailTable from "./DetailTable";

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
                <p className="help-block">
                    Customize the look, feel, and layout of the current visual.
                </p>
                {content}
            </div>
        );
    }
    renderForm() {
        const {
            visualCustomizationPanelActiveTab,
            changeActiveVisualCustomizationTab,
        } = this.props.store.subclass;
        return (
            <Tabs
                selectedIndex={visualCustomizationPanelActiveTab}
                onSelect={changeActiveVisualCustomizationTab}>
                <TabList>
                    <Tab>Heatmap</Tab>
                    <Tab>Filters/Details</Tab>
                    <Tab>Advanced</Tab>
                </TabList>
                <TabPanel>{this.renderHeatmapTab()}</TabPanel>
                <TabPanel>{this.renderFiltersTab()}</TabPanel>
                <TabPanel>{this.renderAdvancedTab()}</TabPanel>
            </Tabs>
        );
    }
    renderHeatmapTab() {
        const {settings, changeSettings} = this.props.store.subclass;
        return (
            <div>
                <h4>Plot labels</h4>
                <div className="row-fluid">
                    <div className="span4">
                        <TextInput
                            name="title.text"
                            label="Title"
                            value={settings.title.text}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />
                    </div>
                    <div className="span4">
                        <TextInput
                            name="x_label.text"
                            label="X-axis label"
                            value={settings.x_label.text}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />
                    </div>
                    <div className="span4">
                        <TextInput
                            name="y_label.text"
                            label="Y-axis label"
                            value={settings.y_label.text}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />
                    </div>
                </div>

                <hr />

                <h4>X fields</h4>
                <AxisLabelTable settingsKey={"x_fields"} />

                <h4>Y fields</h4>
                <AxisLabelTable settingsKey={"y_fields"} />
            </div>
        );
    }
    renderFiltersTab() {
        return (
            <div>
                <h4>Filter widgets</h4>
                <FilterWidgetTable />
                <hr />
                <h4>Table display</h4>
                <DetailTable />
            </div>
        );
    }
    renderAdvancedTab() {
        const {settings, changeSettings} = this.props.store.subclass;
        return (
            <div>
                <h4>Plot</h4>
                <div className="row-fluid">
                    <div className="span3">
                        <FloatInput
                            name="cell_width"
                            label="Cell width"
                            value={settings.cell_width}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span3">
                        <FloatInput
                            name="cell_height"
                            label="Cell height"
                            value={settings.cell_height}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span3">
                        <CheckboxInput
                            id="autosize_cells"
                            label="Auto-size cells"
                            name="autosize_cells"
                            onChange={e => changeSettings(e.target.name, e.target.checked)}
                            checked={settings.autosize_cells}
                        />
                    </div>
                </div>
                <div className="row-fluid">
                    <div className="span3">
                        <FloatInput
                            name="padding.top"
                            label="Padding top"
                            value={settings.padding.top}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span3">
                        <FloatInput
                            name="padding.left"
                            label="Padding left"
                            value={settings.padding.left}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span3">
                        <FloatInput
                            name="padding.bottom"
                            label="Padding bottom"
                            value={settings.padding.bottom}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span3">
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
                <div className="row-fluid">
                    <div className="span3">
                        <TextInput
                            label="Color range (start)"
                            name="color_range1"
                            type="color"
                            value={settings.color_range[0]}
                            onChange={e => changeSettings("color_range.0", e.target.value)}
                        />
                    </div>
                    <div className="span3">
                        <TextInput
                            label="Color range (end)"
                            name="color_range2"
                            type="color"
                            value={settings.color_range[1]}
                            onChange={e => changeSettings("color_range.1", e.target.value)}
                        />
                    </div>
                </div>
                <div className="row-fluid">
                    <div className="span3">
                        <CheckboxInput
                            id="compress_x"
                            label="Compress X fields?"
                            name="compress_x"
                            onChange={e => changeSettings(e.target.name, e.target.checked)}
                            checked={settings.compress_x}
                        />
                    </div>
                    <div className="span3">
                        <CheckboxInput
                            id="compress_y"
                            label="Compress Y fields?"
                            name="compress_y"
                            onChange={e => changeSettings(e.target.name, e.target.checked)}
                            checked={settings.compress_y}
                        />
                    </div>
                    <div className="span3">
                        <CheckboxInput
                            id="show_grid"
                            label="Show cell grid"
                            name="show_grid"
                            onChange={e => changeSettings(e.target.name, e.target.checked)}
                            checked={settings.show_grid}
                        />
                    </div>
                </div>
                <h4>Axes</h4>
                <div className="row-fluid">
                    <div className="span3">
                        <FloatInput
                            name="x_tick_rotate"
                            label="X-axis tick rotation"
                            value={settings.x_tick_rotate}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span3">
                        <FloatInput
                            name="y_tick_rotate"
                            label="Y-axis tick rotation"
                            value={settings.y_tick_rotate}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span3">
                        <CheckboxInput
                            id="autorotate_tick_labels"
                            label="Auto-rotate tick labels"
                            name="autorotate_tick_labels"
                            onChange={e => changeSettings(e.target.name, e.target.checked)}
                            checked={settings.autorotate_tick_labels}
                        />
                    </div>
                </div>
                <div className="row-fluid">
                    <SelectInput
                        handleSelect={value => changeSettings("x_axis_bottom", value == "bottom")}
                        choices={[
                            {id: "top", label: "Top"},
                            {id: "bottom", label: "Bottom"},
                        ]}
                        value={settings.x_axis_bottom ? "bottom" : "top"}
                        multiple={false}
                        label="X-axis position"
                    />
                </div>
                <div className="row-fluid">
                    <div className="span3">
                        <CheckboxInput
                            id="show_axis_border"
                            label="Show axis border"
                            name="show_axis_border"
                            onChange={e => changeSettings(e.target.name, e.target.checked)}
                            checked={settings.show_axis_border}
                        />
                    </div>
                </div>

                <h4>Labels</h4>
                <div className="row-fluid">
                    <div className="span4">
                        <FloatInput
                            name="title.x"
                            label="Title x-coordinate"
                            value={settings.title.x}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span4">
                        <FloatInput
                            name="title.y"
                            label="Title y-coordinate"
                            value={settings.title.y}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span4">
                        <FloatInput
                            name="title.rotate"
                            label="Title rotation"
                            value={settings.title.rotate}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                </div>
                <div className="row-fluid">
                    <div className="span4">
                        <FloatInput
                            name="x_label.x"
                            label="X-axis label x-coordinate"
                            value={settings.x_label.x}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span4">
                        <FloatInput
                            name="x_label.y"
                            label="X-axis label y-coordinate"
                            value={settings.x_label.y}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span4">
                        <FloatInput
                            name="x_label.rotate"
                            label="X-axis label rotation"
                            value={settings.x_label.rotate}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                </div>
                <div className="row-fluid">
                    <div className="span4">
                        <FloatInput
                            name="y_label.x"
                            label="Y-axis label x-coordinate"
                            value={settings.y_label.x}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span4">
                        <FloatInput
                            name="y_label.y"
                            label="Y-axis label y-coordinate"
                            value={settings.y_label.y}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                    <div className="span4">
                        <FloatInput
                            name="y_label.rotate"
                            label="Y-axis label rotation"
                            value={settings.y_label.rotate}
                            onChange={e =>
                                changeSettings(e.target.name, parseFloat(e.target.value))
                            }
                        />
                    </div>
                </div>
                <h4>Interactivity</h4>
                <div className="row-fluid">
                    <div className="span3">
                        <CheckboxInput
                            id="hawc_interactivity"
                            label="HAWC interactivity"
                            name="hawc_interactivity"
                            onChange={e => changeSettings(e.target.name, e.target.checked)}
                            checked={settings.hawc_interactivity}
                        />
                    </div>
                    <div className="span3">
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
        );
    }
}
VisualCustomizationPanel.propTypes = {
    store: PropTypes.object,
};
export default VisualCustomizationPanel;
