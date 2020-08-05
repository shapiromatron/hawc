import React, {Component} from "react";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import {urlLookup} from "./constants";
import h from "shared/utils/helpers";
import AutocompleteSelectableText from "shared/components/AutocompleteSelectableText";

@inject("store")
@observer
class TermSelector extends Component {
    constructor(props) {
        super(props);
        this.randomId = h.randomString();
    }
    render() {
        const {label, termIdField, termTextField, parentIdField, store} = this.props,
            {object} = store.config,
            useControlledVocabulary = store.useControlledVocabulary[termTextField];

        return (
            <div>
                <label className="control-label" htmlFor={this.randomId}>
                    {label}
                </label>
                {useControlledVocabulary ? (
                    <div>
                        <AutocompleteSelectableText
                            url={urlLookup[termIdField]}
                            onChange={text => store.setObjectField(termTextField, text)}
                            value={object[termTextField]}
                            placeholder={"CONTROLLED"}
                        />
                    </div>
                ) : (
                    <AutocompleteSelectableText
                        url={urlLookup[termIdField]}
                        onChange={text => store.setObjectField(termTextField, text)}
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
                <ul>
                    <li>termId: {object[termIdField]}</li>
                    <li>text: {object[termTextField]}</li>
                    <li>parent: {object[parentIdField]}</li>
                </ul>
            </div>
        );
    }
}
TermSelector.propTypes = {
    label: PropTypes.string.isRequired,
    termIdField: PropTypes.string.isRequired,
    termTextField: PropTypes.string.isRequired,
    parentIdField: PropTypes.string,
    store: PropTypes.object,
};

export default TermSelector;

/*
https://github.com/moroshko/react-autosuggest

[x] build current form w/ no vocab autosuggest
[ ] build new form toggle to use other or existing
[ ] build new form toggle w/ vocab
[ ] build debug prop type to show/hide metadata for field
[ ] hook this app into current EndpointForm
[ ] make sure to strip() text for system, organ, effect, effect_subtype, name, etc server side.
    (and add db migration to remove)
*/
