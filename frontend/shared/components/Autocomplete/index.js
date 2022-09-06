import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import AutoSuggest from "react-autosuggest";

import h from "shared/utils/helpers";
import {DEFAULT_MIN_SEARCH_LENGTH, DEBOUNCE_MS, theme} from "../Autocomplete/constants";
import {InlineAutosuggest, renderInlineAutosuggest} from "./Inline";
import "./Autocomplete.css";

class Autocomplete extends Component {
    /*
    An autocomplete field for use with django-autocomplete-light
    */
    constructor(props) {
        super(props);
        let {loaded} = props;
        this.state = {
            suggestions: [],
            currentText: loaded.display ? loaded.display : "",
            currentId: loaded.id ? loaded.id : null,
        };
    }

    onSuggestionsFetchRequested({value}) {
        const {url, minSearchLength} = this.props,
            _minSearchLength = minSearchLength || DEFAULT_MIN_SEARCH_LENGTH;

        if (value.length < _minSearchLength) {
            return;
        }

        fetch(`${url}&q=${value}`, h.fetchGet)
            .then(response => response.json())
            .then(json => this.setState({suggestions: json.results}));
    }

    render() {
        const {suggestions, currentText} = this.state,
            {placeholder, id, onChange} = this.props,
            throttledFetchRequest = _.debounce(
                this.onSuggestionsFetchRequested.bind(this),
                DEBOUNCE_MS
            );
        return (
            <AutoSuggest
                id={id}
                suggestions={suggestions}
                onSuggestionsFetchRequested={throttledFetchRequest}
                onSuggestionsClearRequested={() => this.setState({suggestions: []})}
                onSuggestionSelected={(event, {suggestion}) => {
                    this.setState({currentId: suggestion.id});
                    onChange(suggestion);
                }}
                getSuggestionValue={suggestion => suggestion.text}
                renderSuggestion={suggestion => <span>{suggestion.text}</span>}
                inputProps={{
                    placeholder,
                    className: "form-control",
                    value: currentText,
                    onChange: (event, {newValue}) => {
                        if (newValue === "") {
                            onChange(null);
                        }
                        this.setState({currentText: newValue, selected: null});
                    },
                }}
                theme={theme}
            />
        );
    }
}

Autocomplete.propTypes = {
    id: PropTypes.string.isRequired,
    placeholder: PropTypes.string,
    url: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
    loaded: PropTypes.shape({
        display: PropTypes.string,
        id: PropTypes.number,
    }),
    minSearchLength: PropTypes.number,
};

export {InlineAutosuggest, renderInlineAutosuggest};
export default Autocomplete;
