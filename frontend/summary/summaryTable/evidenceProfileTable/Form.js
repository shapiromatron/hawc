import {observer} from "mobx-react";
import React, {Component} from "react";
import PropTypes from "prop-types";
import {Tab, Tabs, TabList, TabPanel} from "react-tabs";

import EvidenceForm from "./EvidenceForm";
import MechanisticForm from "./MechanisticForm";
import IntegrationForm from "./IntegrationForm";

@observer
class EvidenceProfileForm extends Component {
    render() {
        const {store} = this.props,
            {
                editTabIndex,
                editTabIndexUpdate,
                numEpiJudgementRowSpan,
                numAniJudgementRowSpan,
            } = store;
        return (
            <Tabs selectedIndex={editTabIndex} onSelect={tabIndex => editTabIndexUpdate(tabIndex)}>
                <TabList>
                    <Tab>Human</Tab>
                    <Tab>Animal</Tab>
                    <Tab>Mechanistic</Tab>
                    <Tab>Integration</Tab>
                </TabList>
                <TabPanel>
                    <EvidenceForm
                        store={store}
                        contentType={"exposed_human"}
                        createMethodName={"createHumanRow"}
                        judgementRowSpan={numEpiJudgementRowSpan}
                    />
                </TabPanel>
                <TabPanel>
                    <EvidenceForm
                        store={store}
                        contentType={"animal"}
                        createMethodName={"createAnimalRow"}
                        judgementRowSpan={numAniJudgementRowSpan}
                    />
                </TabPanel>
                <TabPanel>
                    <MechanisticForm store={store} />
                </TabPanel>
                <TabPanel>
                    <IntegrationForm store={store} />
                </TabPanel>
            </Tabs>
        );
    }
}

EvidenceProfileForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default EvidenceProfileForm;
