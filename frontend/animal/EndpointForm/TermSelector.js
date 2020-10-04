import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import {termUrlLookup, textUrlLookup} from "./constants";
import {VOCAB_HELP_TEXT, NO_VOCAB_HELP_TEXT} from "../../vocab/constants";
import h from "shared/utils/helpers";
import AutocompleteSelectableText from "shared/components/AutocompleteSelectableText";
import AutocompleteTerm from "shared/components/AutocompleteTerm";

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
                termIdField,
                termTextField,
                parentIdField,
                store,
                parentRequired,
            } = this.props,
            {object, debug, vocabulary} = store.config,
            useControlledVocabulary = store.useControlledVocabulary[termTextField],
            currentId = object[termIdField],
            currentText = object[termTextField];

        return (
            <div>
                {useControlledVocabulary && idLookupAction ? (
                    <div className="pull-right">
                        <div className="input-append">
                            <input
                                type="number"
                                placeholder="Enter term ID"
                                style={{maxWidth: 100}}
                                value={this.state.idLookupValue}
                                onChange={event =>
                                    this.setState({
                                        idLookupValue: parseInt(event.target.value),
                                    })
                                }></input>
                            <button
                                className="btn"
                                type="button"
                                onClick={() => {
                                    idLookupAction(this.state.idLookupValue);
                                }}>
                                Load ID
                            </button>
                        </div>
                    </div>
                ) : null}
                <label className="control-label" htmlFor={this.randomId}>
                    {label}
                </label>
                {useControlledVocabulary ? (
                    <AutocompleteTerm
                        url={termUrlLookup[termIdField]}
                        onChange={(id, text) => {
                            store.setObjectField(termIdField, id);
                            store.setObjectField(termTextField, text);
                        }}
                        placeholder={VOCAB_HELP_TEXT[vocabulary]}
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
                        <span className="label">
                            {currentId}&nbsp;|&nbsp;{currentText}&nbsp;
                            <button
                                type="button"
                                className="btn btn-mini"
                                title="Unselect term"
                                onClick={() => store.setObjectField(termIdField, null)}>
                                &times;
                            </button>
                        </span>
                        &nbsp;
                        {/* <span
                            className="label label-mini label-important"
                            title="The text presented is different than the selected term">
                            Modified
                        </span> */}
                    </p>
                ) : null}
                {store.canUseControlledVocabulary ? (
                    <label className="checkbox">
                        <input
                            type="checkbox"
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
                ) : null}
                <input type="hidden" name={name + "_term"} value={currentId || ""} />
                <input type="hidden" name={name} value={currentText || ""} />
                <p className="help-block">{helpText}</p>
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
    helpText: PropTypes.string.isRequired,
    termIdField: PropTypes.string.isRequired,
    termTextField: PropTypes.string.isRequired,
    parentIdField: PropTypes.string,
    parentRequired: PropTypes.bool,
    store: PropTypes.object,
    idLookupAction: PropTypes.func,
};

export default TermSelector;
