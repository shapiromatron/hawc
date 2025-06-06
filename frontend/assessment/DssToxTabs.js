import DssToxDetailTable from "assessment/components/DssToxDetailTable";
import DssTox from "assessment/DssTox";
import PropTypes from "prop-types";
import React, {Component} from "react";
import {createRoot} from "react-dom/client";
import {Tab, TabList, TabPanel, Tabs} from "react-tabs";

class DssToxTabs extends Component {
    constructor(props) {
        super(props);
    }
    render() {
        const {objects} = this.props;
        if (objects.length === 0) {
            return null;
        } else if (objects.length === 1) {
            return <DssToxDetailTable object={objects[0]} showHeader={false} />;
        } else {
            return (
                <Tabs>
                    <TabList>
                        {objects.map((object, key) => (
                            <Tab key={key}>{object.data.content.preferredName}</Tab>
                        ))}
                    </TabList>
                    {objects.map((object, key) => (
                        <TabPanel key={key}>
                            <DssToxDetailTable object={object} showHeader={false} />
                        </TabPanel>
                    ))}
                </Tabs>
            );
        }
    }
}
DssToxTabs.propTypes = {
    objects: PropTypes.arrayOf(PropTypes.object),
};

const renderDssToxTabs = function(el, objects) {
    const substances = objects.map(d => new DssTox(d));
    const root = createRoot(el);
    root.render(<DssToxTabs objects={substances} />);
};

export default renderDssToxTabs;
