import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import fetch from "isomorphic-fetch";
import AutoSuggest from "react-autosuggest";

import h from "shared/utils/helpers";
import "../Autocomplete/Autocomplete.css";

const DEFAULT_MIN_SEARCH_LENGTH = 3,
    DEBOUNCE_MS = 500;

class AutocompleteSelectableText extends Component {
    /*
    Autocomplete widget; works with `hawc.apps.common.lookups.DistinctStringLookup`
    */

    constructor(props) {
        super(props);
        this.defaultTheme = {
            container: "autocomplete__container",
            containerOpen: "autocomplete__container--open",
            input: "autocomplete__input",
            suggestionsContainer: "autocomplete__suggestions-container",
            suggestionsList: "autocomplete__suggestions-list",
            suggestion: "autocomplete__suggestion",
            suggestionHighlighted: "autocomplete__suggestion--highlighted",
            sectionContainer: "autocomplete__section-container",
            sectionTitle: "autocomplete__section-title",
        };
        this.state = {
            id: h.randomString(),
            suggestions: [],
            theme: {...this.defaultTheme},
        };
        this.throttledFetchRequest = _.debounce(
            this.onSuggestionsFetchRequested.bind(this),
            DEBOUNCE_MS
        );
    }

    onSuggestionsFetchRequested({value}) {
        const {url, minSearchLength} = this.props,
            _minSearchLength = minSearchLength || DEFAULT_MIN_SEARCH_LENGTH;

        if (value.length < _minSearchLength) {
            return;
        }

        const queryUrl = `${url}&term=${value}`;
        fetch(queryUrl, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                const values = json.map(d => d.name);
                this.setState({suggestions: values});
            });
    }

    render() {
        const {suggestions, theme} = this.state,
            {placeholder, value, onChange} = this.props,
            inputProps = {
                value,
                suggestions,
                placeholder: placeholder || "",
                onChange: (event, {newValue}) => onChange(newValue),
            };
        return (
            <AutoSuggest
                id={this.state.id}
                suggestions={suggestions}
                onSuggestionsFetchRequested={this.throttledFetchRequest}
                onSuggestionsClearRequested={() => this.setState({suggestions: []})}
                getSuggestionValue={suggestion => suggestion}
                renderSuggestion={suggestion => {
                    return (
                        <span
                            dangerouslySetInnerHTML={{
                                __html: suggestion.replace(
                                    new RegExp(this.props.value, "gi"),
                                    match => `<b>${match}</b>`
                                ),
                            }}
                        />
                    );
                }}
                inputProps={inputProps}
                theme={theme}
            />
        );
    }
}

AutocompleteSelectableText.propTypes = {
    url: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    value: PropTypes.string.isRequired,
    placeholder: PropTypes.string,
    minSearchLength: PropTypes.number,
};

export default AutocompleteSelectableText;
