import React from "react";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";
import "react-tabs/style/react-tabs.css";
import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import VisualTab from "./VisualTab";
import DataTab from "./DataTab";
import CustomizeTab from "./CustomizeTab";
import SelectInput from "shared/components/SelectInput";

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
                    <div className="float-right" style={{width: 440}}>
                        <label htmlFor="dashboardSelector">Dashboard:</label>
                        <SelectInput
                            className="form-control d-inline-block h-100 mx-1 py-1"
                            id="dashboardSelector"
                            choices={dashboardOptions}
                            style={{maxWidth: 300}}
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
