import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";

import GlobalSettings from "./GlobalSettings";
import PrismaDataTab from "./PrismaDataTab";

@inject("store")
@observer
class SettingsPanel extends Component {
    render() {
        return (
            <Tabs>
                <TabList>
                    <Tab>Overall</Tab>
                    <Tab>Flowchart</Tab>
                </TabList>
                <TabPanel>
                    <GlobalSettings />
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
