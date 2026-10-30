import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";

import RecommendationsTab from "./RecommendationsTab";
import ResultsTab from "./ResultsTab";
import SetupTab from "./SetupTab";

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
