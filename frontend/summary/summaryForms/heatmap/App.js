import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import FormActions from "shared/components/FormActions";

import OverallTab from "../shared/OverallTab";
import DataPanel from "./DataPanel";
import PreviewPanel from "./PreviewPanel";
import VisualCustomizationPanel from "./VisualCustomizationPanel";

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
                <Tabs onSelect={handleTabSelection}>
                    <TabList>
                        <Tab>Overall</Tab>
                        <Tab>Data</Tab>
                        <Tab>Figure customization</Tab>
                        <Tab>Preview</Tab>
                    </TabList>
                    <TabPanel>
                        <OverallTab
                            legend="Exploratory heatmap settings"
                            helpText="Overall plot settings (eg., title, caption, visibility.)"
                        />
                    </TabPanel>
                    <TabPanel>
                        <DataPanel />
                    </TabPanel>
                    <TabPanel>
                        <VisualCustomizationPanel />
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
