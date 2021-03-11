import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import {label, helpText} from "./constants";
import TermSelector from "./TermSelector";

@inject("store")
@observer
class App extends Component {
    render() {
        const {store} = this.props;
        return (
            <>
                <TermSelector
                    name={"name"}
                    label={label.endpoint_name}
                    helpText={helpText.endpoint_name}
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
