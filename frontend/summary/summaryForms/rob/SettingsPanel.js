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
            {changeSetting} = store;
        return (
            <div className="row">
                <div className="col-4">
                    <TextInput
                        name="zzz"
                        value="zzz"
                        label="Title"
                        onChange={e => changeSetting("z", e.target.value)}
                    />
                </div>
                <div className="col-4">
                    <TextInput
                        name="zzz"
                        value="zzz"
                        label="X-axis Label"
                        onChange={e => changeSetting("z", e.target.value)}
                    />
                </div>
                <div className="col-4">
                    <TextInput
                        name="zzz"
                        value="zzz"
                        label="Y-axis Label"
                        onChange={e => changeSetting("z", e.target.value)}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="styles.section.padding_x"
                        value={1234}
                        label="Padding Top (px)"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="styles.section.padding_x"
                        value={1234}
                        label="Padding Right (px)"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="styles.section.padding_x"
                        value={1234}
                        label="Padding Bottom (px)"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="styles.section.padding_x"
                        value={1234}
                        label="Padding Left (px)"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-3">
                    <IntegerInput
                        name="styles.section.padding_x"
                        value={1234}
                        label="Cell Size (px)"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-3">
                    <SelectInput
                        choices={[
                            {id: "study", label: "Study"},
                            {id: "metric", label: "Metric"},
                        ]}
                        value={"study"}
                        handleSelect={value => changeSetting("", value)}
                        label="X Axis Field"
                    />
                </div>
                <div className="col-3">
                    <SelectInput
                        choices={[
                            {id: "short_citation", label: "Short Citation"},
                            {id: "overall_confidence", label: "Final Study Confidence"},
                        ]}
                        value={"short_citation"}
                        handleSelect={value => changeSetting("", value)}
                        label="Study Sort Order"
                    />
                </div>
                <div className="col-3">
                    <SelectInput
                        choices={[
                            {id: "short_citation", label: "Short Citation"},
                            {id: "study_identifier", label: "Study Identifier"},
                        ]}
                        value={"short_citation"}
                        handleSelect={value => changeSetting("", value)}
                        label="Study Label"
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
class MetricTab extends Component {
    render() {
        const {store} = this.props,
            {changeSetting} = store;
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
                        <tbody></tbody>
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
            {changeSetting} = store;
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
                        <tbody></tbody>
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
            {changeSetting} = store;
        return (
            <div className="row">
                <div className="col-6">
                    <CheckboxInput
                        label="Show Legend"
                        name="..."
                        onChange={e => changeSetting(e.target.name, e.target.checked)}
                        checked={true}
                        helpText={"Overrides cell dimensions for calculated best fit"}
                    />
                </div>
                <div className="col-6"></div>
                <div className="col-6">
                    <CheckboxInput
                        label="Show N/A in legend"
                        name="..."
                        onChange={e => changeSetting(e.target.name, e.target.checked)}
                        checked={true}
                        helpText={'Show "Not applicable" in the legend'}
                    />
                </div>
                <div className="col-6">
                    <CheckboxInput
                        label="Show NR in legend"
                        name="..."
                        onChange={e => changeSetting(e.target.name, e.target.checked)}
                        checked={true}
                        helpText={'Show "Not reported" in the legend'}
                    />
                </div>
                <div className="col-6">
                    <IntegerInput
                        name="styles.section.padding_x"
                        value={1234}
                        label="Legend X Location (px)"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
                    />
                </div>
                <div className="col-6">
                    <IntegerInput
                        name="styles.section.padding_x"
                        value={1234}
                        label="Legend Y Location (px)"
                        onChange={e => changeSetting(e.target.name, e.target.value)}
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
        // TODO - show settings for barchart vs heatmap
        const {store} = this.props;
        return (
            <Tabs selectedIndex={store.activeTab} onSelect={store.changeActiveTab}>
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
