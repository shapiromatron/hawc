import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import fetch from "isomorphic-fetch";
import AutoSuggest from "react-autosuggest";

import h from "shared/utils/helpers";
import {
    DEFAULT_MIN_SEARCH_LENGTH,
    DEBOUNCE_MS,
    theme,
    boldPatternText,
} from "../Autocomplete/constants";
import "../Autocomplete/Autocomplete.css";

class AutocompleteTerm extends Component {
    /*
    Autocomplete widget; works with `hawc.apps.vocab.api.EhvTermViewset`
    */

    constructor(props) {
        super(props);
        this.state = {
            id: h.randomString(),
            suggestions: [],
            currentText: props.currentText ? props.currentText : "",
            currentId: props.currentId ? props.currentId : null,
        };
    }

    UNSAFE_componentWillReceiveProps(nextProps) {
        this.setState({
            currentText: nextProps.currentText,
            currentId: nextProps.currentId,
        });
    }

    onSuggestionsFetchRequested({value}) {
        const {url, minSearchLength, parentId} = this.props,
            _minSearchLength = minSearchLength || DEFAULT_MIN_SEARCH_LENGTH;

        if (value.length < _minSearchLength) {
            return;
        }
        let queryUrl = url;
        if (value) {
            queryUrl = `${queryUrl}&term=${value}`;
        }
        if (parentId) {
            queryUrl = `${queryUrl}&parent=${parentId}`;
        }

        fetch(queryUrl, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.setState({suggestions: json});
            });
    }

    render() {
        const {suggestions, currentText} = this.state,
            {placeholder, onChange, parentId, parentRequired} = this.props,
            throttledFetchRequest = _.debounce(
                this.onSuggestionsFetchRequested.bind(this),
                DEBOUNCE_MS
            );

        if (parentRequired && !parentId) {
            return <p>Parent field required.</p>;
        }

        return (
            <AutoSuggest
                id={this.state.id}
                suggestions={suggestions}
                onSuggestionsFetchRequested={throttledFetchRequest}
                onSuggestionsClearRequested={() => this.setState({suggestions: []})}
                onSuggestionSelected={(_, {suggestion}) => onChange(suggestion.id, suggestion.name)}
                getSuggestionValue={suggestion => suggestion.name}
                shouldRenderSuggestions={shouldRenderSuggestions => true}
                renderSuggestion={suggestion => {
                    return (
                        <span
                            dangerouslySetInnerHTML={{
                                __html: boldPatternText(suggestion.name, currentText),
                            }}
                        />
                    );
                }}
                inputProps={{
                    className: "span12",
                    value: currentText,
                    suggestions,
                    placeholder: placeholder || "",
                    onChange: (event, {newValue}) => {
                        if (newValue === "") {
                            // reset value if empty
                            onChange(null, newValue);
                        }
                        this.setState({currentText: newValue});
                    },
                }}
                theme={theme}
            />
        );
    }
}

AutocompleteTerm.propTypes = {
    url: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    currentId: PropTypes.number,
    currentText: PropTypes.string,
    placeholder: PropTypes.string,
    minSearchLength: PropTypes.number,
    parentId: PropTypes.number,
    parentRequired: PropTypes.bool.isRequired,
};

export default AutocompleteTerm;
