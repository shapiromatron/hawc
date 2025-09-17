import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";
import SelectInput from "shared/components/SelectInput";

import CustomizeTab from "./CustomizeTab";
import DataTab from "./DataTab";
import VisualTab from "./VisualTab";

@inject("store")
@observer
class HeatmapTemplateRoot extends React.Component {
    render() {
        const {selectedDashboard, dashboardOptions, changeDashboard, flipAxes} = this.props.store;
        return (
            <Tabs>
                <TabList>
                    <Tab>Visual</Tab>
                    <Tab>Data</Tab>
                    <Tab>Customize</Tab>
                    <div className="float-right d-flex justify-content-end" style={{width: 450}}>
                        <label htmlFor="dashboardSelector">Dashboard:</label>
                        <SelectInput
                            className="form-control d-inline-block flex-grow-1 h-100 m-1 py-1"
                            id="dashboardSelector"
                            choices={dashboardOptions}
                            multiple={false}
                            handleSelect={value => changeDashboard(value)}
                            value={selectedDashboard.id}
                            fieldOnly={true}
                        />
                        <button
                            className="btn btn-light py-1"
                            onClick={() => flipAxes()}
                            title="flip axes">
                            <i className="fa fa-undo"></i>
                        </button>
                    </div>
                </TabList>
                <TabPanel>
                    <VisualTab />
                </TabPanel>
                <TabPanel>
                    <DataTab />
                </TabPanel>
                <TabPanel>
                    <CustomizeTab />
                </TabPanel>
            </Tabs>
        );
    }
}
HeatmapTemplateRoot.propTypes = {
    store: PropTypes.object,
};

export default HeatmapTemplateRoot;
