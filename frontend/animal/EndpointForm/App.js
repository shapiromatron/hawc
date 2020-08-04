import React, {Component} from "react";
import {action, computed, observable, toJS} from "mobx";
import PropTypes from "prop-types";
import {inject, observer} from "mobx-react";

import Autocomplete from "shared/components/Autocomplete";
import h from "shared/utils/helpers";

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
        // TODO: RESUME here!
        return (
            <div>
                <label className="control-label" htmlFor={this.randomId}>
                    {this.props.label}
                </label>
                {store.useVocabulary ? (
                    <p>controlled (new way; suggest vocab)</p>
                ) : (
                    <p>recommended (old way; selectable-only)</p>
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

@inject("store")
@observer
class App extends Component {
    render() {
        return (
            <div>
                <TermSelector
                    label={"System"}
                    termIdField={"system"}
                    termTextField={"system_term_id"}
                />
                <TermSelector
                    label={"Organ"}
                    termIdField={"organ"}
                    termTextField={"organ_term_id"}
                    parentIdField={"system_term_id"}
                />
                <TermSelector
                    label={"Effect"}
                    termIdField={"effect"}
                    termTextField={"effect_term_id"}
                    parentIdField={"organ_term_id"}
                />
                <TermSelector
                    label={"Effect subtype"}
                    termIdField={"effect_subtype"}
                    termTextField={"effect_subtype_term_id"}
                    parentIdField={"effect_term_id"}
                />
                <TermSelector
                    label={"Endpoint name"}
                    termIdField={"name"}
                    termTextField={"name_term_id"}
                    parentIdField={"effect_subtype_term_id"}
                />
            </div>
        );
    }
}
export default App;
