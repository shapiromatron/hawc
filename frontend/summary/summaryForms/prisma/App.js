import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import FormActions from "shared/components/FormActions";
import UnderDevelopment from "shared/components/UnderDevelopment";

import OverallTab from "../shared/OverallTab";
import PreviewPanel from "./PreviewPanel";
import SettingsPanel from "./SettingsPanel";

@inject("store")
@observer
class App extends Component {
    render() {
        const {cancel_url} = this.props.store.base.config,
            {handleSubmit, handleTabChange} = this.props.store.base,
            handleTabSelection = (newIndex, lastIndex) => {
                handleTabChange(newIndex, lastIndex);
            };

        return (
            <div>
                <UnderDevelopment />
                <Tabs onSelect={handleTabSelection}>
                    <TabList>
                        <Tab>Overall</Tab>
                        <Tab>Settings</Tab>
                        <Tab>Preview</Tab>
                    </TabList>
                    <TabPanel>
                        <OverallTab legend="Prisma Settings" helpText="..." />
                    </TabPanel>
                    <TabPanel>
                        <SettingsPanel />
                    </TabPanel>
                    <TabPanel>
                        <PreviewPanel />
                    </TabPanel>
                </Tabs>
                <FormActions handleSubmit={handleSubmit} cancel={cancel_url} />
            </div>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};
export default App;
