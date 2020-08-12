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
        this.randomId = h.randomString();
    }
    render() {
        const {
                label,
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
                <label className="control-label" htmlFor={this.randomId}>
                    {label}
                </label>
                {useControlledVocabulary ? (
                    <div>
                        <AutocompleteTerm
                            url={termUrlLookup[termIdField]}
                            onChange={(id, text) => {
                                store.setObjectField(termIdField, id);
                                store.setObjectField(termTextField, text);
                            }}
                            placeholder={"CONTROLLED"}
                            currentId={object[termIdField]}
                            currentText={object[termIdField] ? object[termTextField] : ""}
                            parentId={object[parentIdField]}
                            parentRequired={parentRequired}
                            minSearchLength={-1}
                        />
                    </div>
                ) : (
                    <AutocompleteSelectableText
                        url={textUrlLookup[termIdField]}
                        onChange={text => {
                            store.setObjectField(termIdField, null);
                            store.setObjectField(termTextField, text);
                        }}
                        value={object[termTextField]}
                        placeholder={"FREE TEXT"}
                    />
                )}
                {store.canUseControlledVocabulary ? (
                    <label className="checkbox">
                        <input
                            type="checkbox"
                            checked={useControlledVocabulary}
                            onChange={() => store.toggleUseControlledVocabulary(termTextField)}
                        />
                        &nbsp;Use controlled vocabulary
                    </label>
                ) : null}
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
    label: PropTypes.string.isRequired,
    termIdField: PropTypes.string.isRequired,
    termTextField: PropTypes.string.isRequired,
    parentIdField: PropTypes.string,
    parentRequired: PropTypes.bool,
    store: PropTypes.object,
};

export default TermSelector;
