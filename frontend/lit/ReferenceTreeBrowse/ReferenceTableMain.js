import React, {Component} from "react";
import PropTypes from "prop-types";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";
import {inject, observer} from "mobx-react";

import ReferenceTable from "../components/ReferenceTable";
import Wordcloud from "./Wordcloud";

@inject("store")
@observer
class ReferenceTableMain extends Component {
    render() {
        const {store} = this.props,
            {selectedReferences, filteredReferences} = store,
            {canEdit} = store.config;
        if (!selectedReferences) {
            return null;
        }
        return (
            <Tabs
                selectedIndex={store.activeReferenceTableTab}
                onSelect={store.changeActiveReferenceTableTab}>
                <TabList>
                    <Tab>References</Tab>
                    <Tab>Insights</Tab>
                </TabList>
                <TabPanel>
                    <ReferenceTable references={filteredReferences} showActions={canEdit} />
                </TabPanel>
                <TabPanel>
                    <h4>Title wordcloud</h4>
                    <Wordcloud references={filteredReferences} />
                </TabPanel>
            </Tabs>
        );
    }
}
ReferenceTableMain.propTypes = {
    store: PropTypes.object,
};

export default ReferenceTableMain;
