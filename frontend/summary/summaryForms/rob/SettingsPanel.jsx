import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import CheckboxInput from "shared/components/CheckboxInput";
import IntegerInput from "shared/components/IntegerInput";
import SelectInput from "shared/components/SelectInput";
import TextInput from "shared/components/TextInput";

@inject("store")
@observer
class GeneralSettingsTab extends Component {
    render() {
        const {store} = this.props,
            {changeSetting, settings, isHeatmap, isBarchart} = store.subclass;
        return (
            <div className="row">
                <div className="col-4">
                    <TextInput
                        name="title"
                        value={settings.title}
                        label="Title"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-4">
                    <TextInput
                        name="xAxisLabel"
                        value={settings.xAxisLabel}
                        label="X-axis Label"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-4">
                    <TextInput
                        name="yAxisLabel"
                        value={settings.yAxisLabel}
                        label="Y-axis Label"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="padding_top"
                        value={settings.padding_top}
                        label="Padding Top (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="padding_right"
                        value={settings.padding_right}
                        label="Padding Right (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="padding_bottom"
                        value={settings.padding_bottom}
                        label="Padding Bottom (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="padding_left"
                        value={settings.padding_left}
                        label="Padding Left (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                {isHeatmap ? (
                    <>
                        <div className="col-3">
                            <IntegerInput
                                name="cell_size"
                                value={settings.cell_size}
                                label="Cell Size (px)"
                                onChange={e =>
                                    changeSetting(e.target.name, parseInt(e.target.value))
                                }
                            />
                        </div>
                        <div className="col-3">
                            <SelectInput
                                choices={[
                                    {id: "study", label: "Study"},
                                    {id: "metric", label: "Metric"},
                                ]}
                                value={settings.x_field}
                                handleSelect={value => changeSetting("x_field", value)}
                                label="X Axis Field"
                            />
                        </div>
                        <div className="col-3">
                            <SelectInput
                                choices={[
                                    {id: "short_citation", label: "Short Citation"},
                                    {id: "overall_confidence", label: "Final Study Confidence"},
                                ]}
                                value={settings.sort_order}
                                handleSelect={value => changeSetting("sort_order", value)}
                                label="Study Sort Order"
                            />
                        </div>
                        <div className="col-3">
                            <SelectInput
                                choices={[
                                    {id: "short_citation", label: "Short Citation"},
                                    {id: "study_identifier", label: "Study Identifier"},
                                ]}
                                value={settings.study_label_field}
                                handleSelect={value => changeSetting("study_label_field", value)}
                                label="Study Label"
                            />
                        </div>
                    </>
                ) : null}
                {isBarchart ? (
                    <>
                        <div className="col-4">
                            <IntegerInput
                                name="plot_width"
                                value={settings.plot_width}
                                label="Plot Width (px)"
                                onChange={e =>
                                    changeSetting(e.target.name, parseInt(e.target.value))
                                }
                            />
                        </div>
                        <div className="col-4">
                            <IntegerInput
                                name="row_height"
                                value={settings.row_height}
                                label="Row Height (px)"
                                onChange={e =>
                                    changeSetting(e.target.name, parseInt(e.target.value))
                                }
                            />
                        </div>
                        <div className="col-4">
                            <p className="my-1">&nbsp;</p>
                            <CheckboxInput
                                name="show_values"
                                label="Show Values on Plot"
                                onChange={e => changeSetting(e.target.name, e.target.checked)}
                                checked={settings.show_values}
                            />
                        </div>
                    </>
                ) : null}
            </div>
        );
    }
}
GeneralSettingsTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class MetricTab extends Component {
    render() {
        const {store} = this.props,
            {metricTableData, toggleMetricInclusion} = store.subclass;
        return (
            <div className="row">
                <div className="col">
                    <h4>Included Metrics</h4>
                    <table className="table table-sm table-bordered">
                        <colgroup>
                            <col width="10%" />
                            <col width="90%" />
                        </colgroup>
                        <thead>
                            <tr>
                                <th>Display</th>
                                <th>Metric</th>
                            </tr>
                        </thead>
                        <tbody>
                            {metricTableData.map(d => {
                                return (
                                    <tr key={d.id}>
                                        <td>
                                            <CheckboxInput
                                                onChange={e =>
                                                    toggleMetricInclusion(d.id, e.target.checked)
                                                }
                                                checked={d.selected}
                                            />
                                        </td>
                                        <td>{d.name}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }
}
MetricTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class JudgmentTab extends Component {
    render() {
        const {store} = this.props,
            {excludedScoreData, toggleExcludedScores} = store.subclass;
        return (
            <div className="row">
                <div className="col">
                    <h4>Included Judgments</h4>
                    <table className="table table-sm table-bordered">
                        <colgroup>
                            <col width="10%" />
                            <col width="30%" />
                            <col width="30%" />
                            <col width="30%" />
                        </colgroup>
                        <thead>
                            <tr>
                                <th>Display</th>
                                <th>Metric</th>
                                <th>Study</th>
                                <th>Judgment</th>
                            </tr>
                        </thead>
                        <tbody>
                            {excludedScoreData.scores.map(d => {
                                const label = d.is_default ? "<none> (overall)" : d.label,
                                    judgment = `${d.score_label} (${d.score_symbol})`;
                                return (
                                    <tr key={d.id}>
                                        <td>
                                            <CheckboxInput
                                                onChange={e =>
                                                    toggleExcludedScores(d.id, e.target.checked)
                                                }
                                                checked={!excludedScoreData.excluded.has(d.id)}
                                            />
                                        </td>
                                        <td>{d.metric__name}</td>
                                        <td>{d.riskofbias__study__short_citation}</td>
                                        <td>
                                            <p className="score">
                                                <b>Label:</b>&nbsp;{label}
                                                <br />
                                                <b>Judgment:</b>&nbsp;{judgment}
                                            </p>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }
}
JudgmentTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class LegendSettingsTab extends Component {
    render() {
        const {store} = this.props,
            {settings, changeSetting} = store.subclass;
        return (
            <div className="row">
                <div className="col-6">
                    <CheckboxInput
                        label="Show Legend"
                        name="show_legend"
                        onChange={e => changeSetting(e.target.name, e.target.checked)}
                        checked={settings.show_legend}
                        helpText={"Overrides cell dimensions for calculated best fit"}
                    />
                </div>
                <div className="col-6"></div>
                <div className="col-6">
                    <CheckboxInput
                        label="Show N/A in legend"
                        name="show_na_legend"
                        onChange={e => changeSetting(e.target.name, e.target.checked)}
                        checked={settings.show_na_legend}
                        helpText={'Show "Not Applicable" in the legend'}
                    />
                </div>
                <div className="col-6">
                    <CheckboxInput
                        label="Show NR in legend"
                        name="show_nr_legend"
                        onChange={e => changeSetting(e.target.name, e.target.checked)}
                        checked={settings.show_nr_legend}
                        helpText={'Show "Not Reported" in the legend'}
                    />
                </div>
                <div className="col-6">
                    <IntegerInput
                        name="legend_x"
                        value={settings.legend_x}
                        label="Legend X Location (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
                <div className="col-6">
                    <IntegerInput
                        name="legend_y"
                        value={settings.legend_y}
                        label="Legend Y Location (px)"
                        onChange={e => changeSetting(e.target.name, parseInt(e.target.value))}
                    />
                </div>
            </div>
        );
    }
}
LegendSettingsTab.propTypes = {
    store: PropTypes.object,
};

@inject("store")
@observer
class SettingsPanel extends Component {
    render() {
        const {activeTab, changeActiveTab} = this.props.store.subclass;
        return (
            <Tabs selectedIndex={activeTab} onSelect={changeActiveTab}>
                <TabList>
                    <Tab>General Settings</Tab>
                    <Tab>Included Metrics</Tab>
                    <Tab>Included Judgments</Tab>
                    <Tab>Legend Settings</Tab>
                </TabList>
                <TabPanel>
                    <GeneralSettingsTab />
                </TabPanel>
                <TabPanel>
                    <MetricTab />
                </TabPanel>
                <TabPanel>
                    <JudgmentTab />
                </TabPanel>
                <TabPanel>
                    <LegendSettingsTab />
                </TabPanel>
            </Tabs>
        );
    }
}
SettingsPanel.propTypes = {
    store: PropTypes.object,
};
export default SettingsPanel;
