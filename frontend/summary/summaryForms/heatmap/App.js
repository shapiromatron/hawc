import PropTypes from "prop-types";
import React, {Component} from "react";
import {inject, observer} from "mobx-react";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";
import OverallPanel from "./OverallPanel";

@inject("store")
@observer
class App extends Component {
    render() {
        const {cancel_url} = this.props.store.base.config,
            {handleSubmit} = this.props.store.base;

        return (
            <div>
                <Tabs onSelect={this.handleTabSelection}>
                    <TabList>
                        <Tab>Overall</Tab>
                        <Tab>Data</Tab>
                        <Tab>Figure customization</Tab>
                        <Tab>Preview</Tab>
                    </TabList>
                    <TabPanel>
                        <OverallPanel />
                    </TabPanel>
                    <TabPanel>
                        <h1>Data</h1>
                    </TabPanel>
                    <TabPanel>
                        <h1>Figure customization</h1>
                    </TabPanel>
                    <TabPanel>
                        <h1>Preview</h1>
                    </TabPanel>
                </Tabs>
                <div className="form-actions">
                    <input
                        type="submit"
                        name="save"
                        value="Save"
                        className="btn btn-primary"
                        onClick={handleSubmit}
                    />
                    <span>&nbsp;</span>
                    <a role="button" className="btn btn-default" href={cancel_url}>
                        Cancel
                    </a>
                </div>
            </div>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};
export default App;
