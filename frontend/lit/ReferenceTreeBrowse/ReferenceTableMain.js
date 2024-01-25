import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";

import ReferenceTable from "../components/ReferenceTable";
import Wordcloud from "./Wordcloud";

@inject("store")
@observer
class ReferenceTableMain extends Component {
    render() {
        const {store} = this.props,
            {selectedReferences, filteredReferences, paginatedReferences, page, fetchPage} = store,
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
                    <ReferenceTable references={paginatedReferences} showActions={canEdit} page={page} fetchPage={fetchPage} />
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
