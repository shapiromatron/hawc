import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import { Tabs, Tab, TabList, TabPanel } from "react-tabs";
import TextInput from "shared/components/TextInput";
import PrismaDataTab from "./PrismaDataTab"

@inject("store")
@observer
class SettingsPanel extends Component {
    render() {
        const {settings, changeSettings} = this.props.store.subclass;
        return (
            <Tabs>
            <TabList>
                <Tab>Data</Tab>
                <Tab>Other Settings</Tab>
            </TabList>
            <TabPanel>
                <PrismaDataTab></PrismaDataTab>
            </TabPanel>
            <TabPanel>
                <div>
                    <legend>Prisma Settings</legend>
                    <p className="form-text text-muted">....</p>
                    <TextInput
                        name="title"
                        label="Plot Title"
                        value={settings.title}
                        onChange={e => changeSettings(e.target.name, e.target.value)} />
                </div>
            </TabPanel>
            </Tabs>
        );
    }
}
SettingsPanel.propTypes = {
    store: PropTypes.object,
};
export default SettingsPanel;
