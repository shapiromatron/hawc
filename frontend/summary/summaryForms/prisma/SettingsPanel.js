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
        const {store} = this.props;
        return (
            <Tabs
                selectedIndex={store.subclass.activeTab}
                onSelect={store.subclass.changeActiveTab}>
                <TabList>
                    <Tab>Flowchart</Tab>
                    <Tab>Styling</Tab>
                </TabList>
                <TabPanel>
                    <PrismaDataTab />
                </TabPanel>
                <TabPanel>
                    <GlobalSettings />
                </TabPanel>
            </Tabs>
        );
    }
}
SettingsPanel.propTypes = {
    store: PropTypes.object,
};
export default SettingsPanel;
