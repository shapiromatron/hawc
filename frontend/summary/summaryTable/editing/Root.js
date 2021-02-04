import {inject, observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";

import Table from "../genericTable/Table";
import TableForm from "../genericTable/TableForm";

import DjangoForm from "./DjangoForm";

@inject("store")
@observer
class Root extends Component {
    render() {
        const {tableStore} = this.props.store;
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
                    <TableForm store={tableStore} />
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
