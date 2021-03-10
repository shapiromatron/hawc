import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";

import {getEditTableComponent, getViewTableComponent} from "../lookups";
import DjangoForm from "./DjangoForm";

@inject("store")
@observer
class Root extends Component {
    render() {
        const {tableStore, tableObject} = this.props.store,
            Form = getEditTableComponent(tableObject),
            Table = getViewTableComponent(tableObject);

        return (
            <Tabs>
                <TabList>
                    <Tab>Overall</Tab>
                    <Tab>Editing</Tab>
                    <Tab>Preview</Tab>
                </TabList>
                <TabPanel>
                    <DjangoForm />
                </TabPanel>
                <TabPanel>
                    <Form store={tableStore} />
                </TabPanel>
                <TabPanel>
                    <Table store={tableStore} forceReadOnly={true} />
                </TabPanel>
            </Tabs>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
