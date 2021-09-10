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
        const {tableStore, tableObject, isCreate, handleSubmit, cancelUrl} = this.props.store,
            saveBtnText = isCreate ? "Create" : "Update",
            Form = getEditTableComponent(tableObject),
            Table = getViewTableComponent(tableObject);

        return (
            <>
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
                <div className="form-actions">
                    <button type="button" onClick={handleSubmit} className="btn btn-primary mr-1">
                        {saveBtnText}
                    </button>
                    <a href={cancelUrl} className="btn btn-light">
                        Cancel
                    </a>
                </div>
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
