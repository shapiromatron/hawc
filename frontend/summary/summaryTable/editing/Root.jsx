import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import FormActions from "shared/components/FormActions";

import {getEditTableComponent, getTableDataComponent, getViewTableComponent} from "../lookups";
import DjangoForm from "./DjangoForm";

@inject("store")
@observer
class Root extends Component {
    render() {
        const {tableStore, tableObject, isCreate, handleSubmit, cancelUrl} = this.props.store,
            saveBtnText = isCreate ? "Create" : "Update",
            Form = getEditTableComponent(tableObject),
            Data = getTableDataComponent(tableObject),
            Table = getViewTableComponent(tableObject);

        return (
            <>
                <Tabs>
                    <TabList>
                        <Tab>Overall</Tab>
                        {Data ? <Tab>Data</Tab> : null}
                        <Tab>Editing</Tab>
                        <Tab>Preview</Tab>
                    </TabList>
                    <TabPanel>
                        <DjangoForm />
                    </TabPanel>
                    {Data ? (
                        <TabPanel>
                            <Data store={tableStore} />
                        </TabPanel>
                    ) : null}
                    <TabPanel>
                        <Form store={tableStore} />
                    </TabPanel>
                    <TabPanel>
                        <Table store={tableStore} forceReadOnly={true} />
                        <div dangerouslySetInnerHTML={{__html: tableObject.caption}} />
                    </TabPanel>
                </Tabs>
                <FormActions
                    handleSubmit={handleSubmit}
                    submitText={saveBtnText}
                    cancel={cancelUrl}
                />
            </>
        );
    }
}

Root.propTypes = {
    store: PropTypes.object,
};

export default Root;
