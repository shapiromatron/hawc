import "./Autocomplete/Autocomplete.css";

import _ from "lodash";
import PropTypes from "prop-types";
import React, {Component} from "react";
import AutoSuggest from "react-autosuggest";
import h from "shared/utils/helpers";

import {
    boldPatternText,
    DEBOUNCE_MS,
    DEFAULT_MIN_SEARCH_LENGTH,
    theme,
} from "./Autocomplete/constants";

class AutocompleteSelectableText extends Component {
    /*
    Autocomplete widget; works with django-autocomplete-light
    */

    constructor(props) {
        super(props);
        this.state = {
            id: h.randomString(),
            suggestions: [],
        };
    }

    onSuggestionsFetchRequested({value}) {
        const {url, minSearchLength} = this.props,
            _minSearchLength = minSearchLength || DEFAULT_MIN_SEARCH_LENGTH;

        if (value.length < _minSearchLength) {
            return;
        }

        const queryUrl = `${url}&q=${value}`;
        fetch(queryUrl, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                const values = json.results.map(d => d.text);
                this.setState({suggestions: values});
            });
    }

    render() {
        const {suggestions} = this.state,
            {placeholder, value, onChange} = this.props,
            throttledFetchRequest = _.debounce(
                this.onSuggestionsFetchRequested.bind(this),
                DEBOUNCE_MS
            );
        return (
            <AutoSuggest
                id={this.state.id}
                suggestions={suggestions}
                onSuggestionsFetchRequested={throttledFetchRequest}
                onSuggestionsClearRequested={() => this.setState({suggestions: []})}
                getSuggestionValue={suggestion => suggestion}
                renderSuggestion={suggestion => {
                    return (
                        <span
                            dangerouslySetInnerHTML={{
                                __html: boldPatternText(suggestion, this.props.value),
                            }}
                        />
                    );
                }}
                inputProps={{
                    value,
                    suggestions,
                    className: "form-control mb-2",
                    placeholder: placeholder || "",
                    onChange: (_event, {newValue}) => onChange(newValue),
                }}
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
