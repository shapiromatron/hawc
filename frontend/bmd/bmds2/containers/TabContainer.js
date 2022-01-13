import React from "react";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";

import {Tab, Tabs, TabList, TabPanel} from "react-tabs";

import SetupTab from "./SetupTab";
import ResultsTab from "./ResultsTab";
import RecommendationsTab from "./RecommendationsTab";

@inject("store")
@observer
class TabContainer extends React.Component {
    render() {
        const {hasExecuted} = this.props.store;

        return (
            <Tabs>
                <TabList>
                    <Tab>BMD setup</Tab>
                    <Tab className="react-tabs__tab bmdResultsTab" disabled={!hasExecuted}>
                        Results
                    </Tab>
                    <Tab disabled={!hasExecuted}>Model recommendation and selection</Tab>
                </TabList>
                <TabPanel>
                    <SetupTab />
                </TabPanel>
                <TabPanel>
                    <ResultsTab />
                </TabPanel>
                <TabPanel>
                    <RecommendationsTab />
                </TabPanel>
            </Tabs>
        );
    }
}
TabContainer.propTypes = {
    store: PropTypes.object,
};
export default TabContainer;
