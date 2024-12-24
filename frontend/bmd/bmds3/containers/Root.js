import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import Loading from "shared/components/Loading";

import ResultTab from "../components/ResultTab";
import SettingsTab from "../components/SettingsTab";

@inject("store")
@observer
class Root extends React.Component {
    componentDidMount() {
        const {store} = this.props;
        store.fetchSession();
    }
    render() {
        const {store} = this.props,
            {hasOutputs} = store,
            defaultTabIndex = hasOutputs ? 1 : 0;

        if (!store.hasSessionLoaded) {
            return <Loading />;
        }

        return (
            <Tabs defaultIndex={defaultTabIndex}>
                <TabList>
                    <Tab>Settings</Tab>
                    <Tab className="react-tabs__tab bmd-results-tab">Results</Tab>
                </TabList>
                <TabPanel>
                    <SettingsTab />
                </TabPanel>
                <TabPanel>
                    <ResultTab />
                </TabPanel>
            </Tabs>
        );
    }
}
Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
