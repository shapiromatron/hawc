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
                    <div className="pull-right">
                        <b>Dashboard selection:&nbsp;</b>
                        <SelectInput
                            name="dashboard"
                            choices={dashboardOptions}
                            multiple={false}
                            handleSelect={value => changeDashboard(value)}
                            value={selectedDashboard.id}
                            fieldOnly={true}
                        />
                        <button
                            style={{marginBottom: 10}}
                            className="btn"
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
