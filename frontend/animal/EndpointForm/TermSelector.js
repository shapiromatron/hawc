import {inject, observer} from "mobx-react";
import PropTypes from "prop-types";
import React, {Component} from "react";
import AutocompleteSelectableText from "shared/components/AutocompleteSelectableText";
import AutocompleteTerm from "shared/components/AutocompleteTerm";
import HelpTextPopup from "shared/components/HelpTextPopup";
import h from "shared/utils/helpers";

import {NO_VOCAB_HELP_TEXT} from "../../vocab/constants";
import {termUrlLookup, textUrlLookup} from "./constants";

@inject("store")
@observer
class TermSelector extends Component {
    constructor(props) {
        super(props);
        this.state = {
            idLookupValue: props.store.config.object[props.termIdField],
        };
        this.randomId = h.randomString();
    }
    render() {
        const {
                idLookupAction,
                name,
                label,
                helpText,
                popupHelpText,
                termIdField,
                termTextField,
                parentIdField,
                store,
                parentRequired,
            } = this.props,
            {object, debug, vocabulary_display} = store.config,
            useControlledVocabulary = store.useControlledVocabulary[termTextField],
            currentId = object[termIdField],
            currentText = object[termTextField];

        return (
            <div className="form-group">
                {useControlledVocabulary && idLookupAction ? (
                    <div className="float-right">
                        <div className="input-group">
                            <input
                                type="number"
                                className="form-control"
                                placeholder="Enter term ID"
                                style={{maxWidth: 130}}
                                value={this.state.idLookupValue}
                                onChange={event =>
                                    this.setState({
                                        idLookupValue: parseInt(event.target.value),
                                    })
                                }></input>
                            <div className="input-group-append">
                                <button
                                    className="btn btn-light"
                                    type="button"
                                    onClick={() => {
                                        idLookupAction(this.state.idLookupValue);
                                    }}>
                                    Load ID
                                </button>
                            </div>
                        </div>
                    </div>
                ) : null}
                <label htmlFor={this.randomId}>{label}</label>
                {popupHelpText ? <HelpTextPopup content={popupHelpText} title={label} /> : null}
                {useControlledVocabulary ? (
                    <AutocompleteTerm
                        url={termUrlLookup[termIdField]}
                        onChange={(id, text) => {
                            store.setObjectField(termIdField, id);
                            store.setObjectField(termTextField, text);
                        }}
                        placeholder={vocabulary_display}
                        currentId={currentId}
                        currentText={currentText}
                        parentId={object[parentIdField]}
                        parentRequired={parentRequired}
                        minSearchLength={-1}
                    />
                ) : (
                    <AutocompleteSelectableText
                        url={textUrlLookup[termIdField]}
                        onChange={text => {
                            store.setObjectField(termIdField, null);
                            store.setObjectField(termTextField, text);
                        }}
                        value={currentText}
                        placeholder={NO_VOCAB_HELP_TEXT}
                    />
                )}
                {object[termIdField] ? (
                    <p>
                        <b>Selected term:</b>&nbsp;
                        <span className="badge badge-secondary px-2 py-0">
                            {currentId}&nbsp;|&nbsp;{currentText}&nbsp;
                            <button
                                type="button"
                                className="btn btn-secondary btn-sm"
                                title="Unselect term"
                                onClick={() => store.setObjectField(termIdField, null)}>
                                &times;
                            </button>
                        </span>
                    </p>
                ) : null}
                {store.canUseControlledVocabulary ? (
                    <div className="form-check">
                        <label>
                            <input
                                type="checkbox"
                                className="form-check-input"
                                checked={useControlledVocabulary}
                                onChange={() => {
                                    const newUseVocab = !useControlledVocabulary;
                                    store.toggleUseControlledVocabulary(termTextField);
                                    if (newUseVocab === false) {
                                        store.setObjectField(termIdField, null);
                                    }
                                }}
                            />
                            &nbsp;Use controlled vocabulary
                        </label>
                    </div>
                ) : null}
                <input type="hidden" name={name + "_term"} value={currentId || ""} />
                <input type="hidden" name={name} value={currentText || ""} />
                {helpText ? (
                    <small
                        className="form-text text-muted"
                        dangerouslySetInnerHTML={{__html: helpText}}></small>
                ) : null}
                {debug ? (
                    <ul>
                        <li>termId: {currentId}</li>
                        <li>text: {currentText}</li>
                        <li>parent: {object[parentIdField]}</li>
                    </ul>
                ) : null}
            </div>
        );
    }
}
TermSelector.propTypes = {
    name: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    helpText: PropTypes.string,
    popupHelpText: PropTypes.string,
    termIdField: PropTypes.string.isRequired,
    termTextField: PropTypes.string.isRequired,
    parentIdField: PropTypes.string,
    parentRequired: PropTypes.bool,
    store: PropTypes.object,
    idLookupAction: PropTypes.func,
};

export default TermSelector;
