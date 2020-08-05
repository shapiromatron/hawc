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
            {object} = store.config;
        return (
            <div>
                <label className="control-label" htmlFor={this.randomId}>
                    {label}
                </label>
                {store.useVocabulary ? (
                    <p>controlled (new way; suggest vocab)</p>
                ) : (
                    <AutocompleteSelectableText
                        url={urlLookup[termIdField]}
                        onChange={text => store.setObjectField(termTextField, text)}
                        value={object[termTextField]}
                        placeholder={"eg., system"}
                    />
                )}
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

1. build current form w/ no vocab autosuggest
2. build new form toggle to use other or existing
3. build new form toggle w/ vocab
4. build debug prop type to show/hide metadata for field
5. hook this app into current EndpointForm
*/
