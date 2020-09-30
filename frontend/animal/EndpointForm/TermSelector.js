import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import {termUrlLookup, textUrlLookup} from "./constants";
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
            {object, debug} = store.config,
            useControlledVocabulary = store.useControlledVocabulary[termTextField];

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
                        placeholder={"(controlled vocab.)"}
                        currentId={object[termIdField]}
                        currentText={object[termIdField] ? object[termTextField] : ""}
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
                        value={object[termTextField]}
                        placeholder={"(semi-controlled vocab.)"}
                    />
                )}
                {object[termIdField] ? (
                    <p>
                        <b>Selected term:</b>
                        &nbsp;<span className="label label-mini">{object[termIdField]}</span>
                        &nbsp;{object[termTextField]}
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
                <input type="hidden" name={name + "_term"} value={object[termIdField] || ""} />
                <input type="hidden" name={name} value={object[termTextField] || ""} />
                <p className="help-block">{helpText}</p>
                {debug ? (
                    <ul>
                        <li>termId: {object[termIdField]}</li>
                        <li>text: {object[termTextField]}</li>
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
