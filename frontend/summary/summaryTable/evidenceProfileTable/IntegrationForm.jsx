import {observer} from "mobx-react";
import PropTypes from "prop-types";
import React from "react";
import CheckboxInput from "shared/components/CheckboxInput";
import QuillTextInput from "shared/components/QuillTextInput";
import TextInput from "shared/components/TextInput";

import {CUSTOM_JUDGEMENT, HELP_TEXT} from "./common";
import {JudgementSelector} from "./Judgement";

const IntegrationForm = observer(props => {
    const {store} = props,
        {summary_judgement} = props.store.settings;

    return (
        <>
            <CheckboxInput
                label="Hide section?"
                checked={summary_judgement.hide_content}
                onChange={e => {
                    store.updateValue("summary_judgement.hide_content", e.target.checked);
                }}
                helpText={HELP_TEXT.HIDE_CONTENT}
                required
            />
            <div className={summary_judgement.hide_content ? "form-row hidden" : "form-row"}>
                <div className="col-md-6">
                    <JudgementSelector
                        value={summary_judgement.judgement}
                        handleSelect={value =>
                            store.updateValue("summary_judgement.judgement", parseInt(value))
                        }
                        helpText={HELP_TEXT.IRIS_HANDBOOK}
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
                        onChange={value =>
                            store.updateValue("summary_judgement.description", value)
                        }
                    />
                </div>
                <div className="col-md-6">
                    <QuillTextInput
                        label="Human relevance"
                        helpText="Use ‘N/A, judgments driven by human data’ or explain the interpretation of the relevance of the animal data to humans. In many cases, a statement such as, ‘without evidence to the contrary, [health effect described in the table] responses in animals are presumed to be relevant to humans’. If possible, include some brief text describing the interpreted comparability of experimental animal organs/systems to humans based on underlying biological similarity (e.g., thyroid signaling processes are well conserved across rodents and humans)."
                        value={summary_judgement.human_relevance}
                        onChange={value =>
                            store.updateValue("summary_judgement.human_relevance", value)
                        }
                    />
                </div>
                <div className="col-md-6">
                    <QuillTextInput
                        label="Cross-stream coherence"
                        helpText="Addresses the biological concordance of findings across human, animal, and mechanistic studies, considering factors such as exposure timing and levels. Notably, for many health effects (e.g., some nervous system and reproductive effects), effects manifest in animals are not expected to be manifest similarly in humans. Please consult and cite guidance and other resources when drawing these inferences."
                        value={summary_judgement.cross_stream_coherence}
                        onChange={value =>
                            store.updateValue("summary_judgement.cross_stream_coherence", value)
                        }
                    />
                </div>

                <div className="col-md-6">
                    <QuillTextInput
                        label="Susceptibility"
                        helpText="Use ‘no evidence to inform’ or include specific evidence-based documentation of potential susceptible populations or lifestages, with brief rationale."
                        value={summary_judgement.susceptibility}
                        onChange={value =>
                            store.updateValue("summary_judgement.susceptibility", value)
                        }
                    />
                </div>
                <div className="col-md-6">
                    <QuillTextInput
                        label="Biological plausibility"
                        helpText="Mechanistic support for biological plausibility"
                        value={summary_judgement.plausibility}
                        onChange={value =>
                            store.updateValue("summary_judgement.plausibility", value)
                        }
                    />
                </div>

                <div className="col-md-6">
                    <QuillTextInput
                        label="Other inferences"
                        helpText="ADME, Other Mode of Action (MOA) analysis inferences (e.g., judgments relevant to dose response analysis), relevant information from other sources (e.g., read across)"
                        value={summary_judgement.other}
                        onChange={value => store.updateValue("summary_judgement.other", value)}
                    />
                </div>
            </div>
        </>
    );
});

IntegrationForm.propTypes = {
    store: PropTypes.object.isRequired,
};

export default IntegrationForm;
