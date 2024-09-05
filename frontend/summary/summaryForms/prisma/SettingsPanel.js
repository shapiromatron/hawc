import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import TextInput from "shared/components/TextInput";

import PrismaDataTab from "./PrismaDataTab";

@inject("store")
@observer
class SettingsPanel extends Component {
    render() {
        const {settings, changeSettings} = this.props.store.subclass;
        return (
            <Tabs>
                <TabList>
                    <Tab>Overall</Tab>
                    <Tab>Flowchart</Tab>
                </TabList>
                <TabPanel>
                    <div>
                        <TextInput
                            name="title"
                            label="Plot Title"
                            value={settings.title}
                            onChange={e => changeSettings(e.target.name, e.target.value)}
                        />
                    </div>
                </TabPanel>
                <TabPanel>
                    <PrismaDataTab />
                </TabPanel>
            </Tabs>
        );
    }
}
SettingsPanel.propTypes = {
    store: PropTypes.object,
};
export default SettingsPanel;
