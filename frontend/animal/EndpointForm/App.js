import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import {helpText, label} from "./constants";
import TermSelector from "./TermSelector";

@inject("store")
@observer
class App extends Component {
    render() {
        const {store} = this.props,
            helpTextName = store.canUseControlledVocabulary
                ? helpText.endpoint_name_ehv
                : helpText.endpoint_name_no_ehv;
        return (
            <>
                <TermSelector
                    name={"name"}
                    label={label.endpoint_name}
                    helpText={helpTextName}
                    popupHelpText={helpText.endpoint_name_popup}
                    termIdField={"name_term_id"}
                    termTextField={"name"}
                    parentIdField={"effect_subtype_term_id"}
                    parentRequired={true}
                    idLookupAction={store.endpointNameLookup}
                />
                <div className="row">
                    <div className="col-md-3">
                        <TermSelector
                            name={"system"}
                            label={label.system}
                            helpText={helpText.system}
                            popupHelpText={helpText.system_popup}
                            termIdField={"system_term_id"}
                            termTextField={"system"}
                            parentRequired={false}
                        />
                    </div>
                    <div className="col-md-3">
                        <TermSelector
                            name={"organ"}
                            label={label.organ}
                            helpText={helpText.organ}
                            popupHelpText={helpText.organ_popup}
                            termIdField={"organ_term_id"}
                            termTextField={"organ"}
                            parentIdField={"system_term_id"}
                            parentRequired={true}
                        />
                    </div>
                    <div className="col-md-3">
                        <TermSelector
                            name={"effect"}
                            label={label.effect}
                            helpText={helpText.effect}
                            popupHelpText={helpText.effect_popup}
                            termIdField={"effect_term_id"}
                            termTextField={"effect"}
                            parentIdField={"organ_term_id"}
                            parentRequired={true}
                        />
                    </div>
                    <div className="col-md-3">
                        <TermSelector
                            name={"effect_subtype"}
                            label={label.effect_subtype}
                            helpText={helpText.effect_subtype}
                            popupHelpText={helpText.effect_subtype_popup}
                            termIdField={"effect_subtype_term_id"}
                            termTextField={"effect_subtype"}
                            parentIdField={"effect_term_id"}
                            parentRequired={true}
                        />
                    </div>
                </div>
            </>
        );
    }
}
App.propTypes = {
    store: PropTypes.object,
};

export default App;
