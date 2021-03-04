import {observer} from "mobx-react";
import React from "react";
import PropTypes from "prop-types";

import TextInput from "shared/components/TextInput";
import QuillTextInput from "shared/components/QuillTextInput";
import {JudgementSelector} from "./Judgement";

import {CUSTOM_JUDGEMENT} from "./common";

const IntegrationForm = observer(props => {
    const {store} = props,
        {summary_judgement} = props.store.settings;

    return (
        <div className="form-row">
            <div className="col-md-6">
                <JudgementSelector
                    value={summary_judgement.judgement}
                    handleSelect={value =>
                        store.updateValue("summary_judgement.judgement", parseInt(value))
                    }
                    summary={true}
                />
            </div>
            <div className="col-md-6">
                {summary_judgement.judgement === CUSTOM_JUDGEMENT ? (
                    <div className="form-row">
                        <div className="col-md-6">
                            <TextInput
                                name="custom_judgement_icon"
                                label="Custom icon"
                                value={summary_judgement.custom_judgement_icon}
                                onChange={e =>
                                    store.updateValue(
                                        "summary_judgement.custom_judgement_icon",
                                        e.target.value
                                    )
                                }
                                required
                            />
                        </div>
                        <div className="col-md-6">
                            <TextInput
                                name="custom_judgement_label"
                                label="Custom label"
                                value={summary_judgement.custom_judgement_label}
                                onChange={e =>
                                    store.updateValue(
                                        "summary_judgement.custom_judgement_label",
                                        e.target.value
                                    )
                                }
                                required
                            />
                        </div>
                    </div>
                ) : null}
            </div>

            <div className="col-md-6">
                <QuillTextInput
                    label="Description"
                    helpText="Enter the overall summary of expert interpretation across the assessed set of biological events, potential mechanisms of toxicity, or other analysis approach (e.g., AOP). Include the primary evidence supporting the interpretation(s).  Describe and substantiate the extent to which the evidence influences inferences across evidence streams. Characterize the limitations of the analyses and highlight data gaps. May have overlap with factors summarized for other streams"
                    value={summary_judgement.description}
                    onChange={value => store.updateValue("summary_judgement.description", value)}
                />
            </div>
            <div className="col-md-6">
                <QuillTextInput
                    label="Susceptibility"
                    helpText="..."
                    value={summary_judgement.susceptibility}
                    onChange={value => store.updateValue("summary_judgement.susceptibility", value)}
                />
            </div>
            <div className="col-md-6">
                <QuillTextInput
                    label="Human relevance"
                    helpText="..."
                    value={summary_judgement.human_relevance}
                    onChange={value =>
                        store.updateValue("summary_judgement.human_relevance", value)
                    }
                />
            </div>
            <div className="col-md-6">
                <QuillTextInput
                    label="Cross-stream coherence"
                    helpText="..."
                    value={summary_judgement.cross_stream_coherence}
                    onChange={value =>
                        store.updateValue("summary_judgement.cross_stream_coherence", value)
                    }
                />
            </div>
        </div>
    );
});

IntegrationForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default IntegrationForm;
