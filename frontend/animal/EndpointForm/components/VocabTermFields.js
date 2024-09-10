import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";

import {defaultHelpText} from "../constants";
import TermSelector from "../TermSelector";

@inject("store")
@observer
class VocabTermFields extends Component {
    render() {
        const {store, termFields} = this.props,
            label = termFields.label,
            termParent = termFields.parent_id,
            helpText = termFields.helpText,
            helpTextName = store.canUseControlledVocabulary
                ? helpText.endpoint_name
                : defaultHelpText.endpoint_name,
            rowClass = label.organ ? "col-md-3" : "col-md-4";
        return (
            <>
                {label.endpoint_name ? (
                    <TermSelector
                        name={"name"}
                        label={label.endpoint_name}
                        helpText={helpTextName}
                        popupHelpText={helpText.endpoint_name_popup}
                        termIdField={"name_term_id"}
                        termTextField={"name"}
                        parentIdField={termParent.endpoint_name_parent}
                        parentRequired={true}
                        idLookupAction={store.endpointNameLookup}
                    />
                ) : null}

                <div className="row">
                    <div className={rowClass}>
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
                    {label.organ ? (
                        <div className={rowClass}>
                            <TermSelector
                                name={"organ"}
                                label={label.organ ? label.organ : ""}
                                helpText={helpText.organ}
                                popupHelpText={helpText.organ_popup}
                                termIdField={"organ_term_id"}
                                termTextField={"organ"}
                                parentIdField={termParent.organ_parent}
                                parentRequired={true}
                            />
                        </div>
                    ) : null}
                    <div className={rowClass}>
                        <TermSelector
                            name={"effect"}
                            label={label.effect}
                            helpText={helpText.effect}
                            popupHelpText={helpText.effect_popup}
                            termIdField={"effect_term_id"}
                            termTextField={"effect"}
                            parentIdField={termParent.effect_parent}
                            parentRequired={true}
                        />
                    </div>
                    <div className={rowClass}>
                        <TermSelector
                            name={"effect_subtype"}
                            label={label.effect_subtype}
                            helpText={helpText.effect_subtype}
                            popupHelpText={helpText.effect_subtype_popup}
                            termIdField={"effect_subtype_term_id"}
                            termTextField={"effect_subtype"}
                            parentIdField={termParent.effect_subtype_parent}
                            parentRequired={true}
                        />
                    </div>
                </div>
            </>
        );
    }
}
VocabTermFields.propTypes = {
    store: PropTypes.object,
    termFields: PropTypes.object,
};

export default VocabTermFields;
