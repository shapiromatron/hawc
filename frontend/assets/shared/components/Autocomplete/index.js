import _ from "lodash";
import React, {Component} from "react";
import PropTypes from "prop-types";
import fetch from "isomorphic-fetch";
import AutoSuggest from "react-autosuggest";

import h from "shared/utils/helpers";
import {DEFAULT_MIN_SEARCH_LENGTH, DEBOUNCE_MS, theme} from "../Autocomplete/constants";
import "./Autocomplete.css";

class Autocomplete extends Component {
    constructor(props) {
        super(props);
        let {loaded} = props;
        this.state = {
            value: loaded.display ? loaded.display : "",
            suggestions: [],
            selected: loaded.id ? loaded.id : null,
        };
    }

    onSuggestionsFetchRequested({value}) {
        const {url, minSearchLength} = this.props,
            _minSearchLength = minSearchLength || DEFAULT_MIN_SEARCH_LENGTH;

        if (value.length < _minSearchLength) {
            return;
        }

        fetch(`${url}&term=${value}`, h.fetchGet)
            .then(response => response.json())
            .then(json => this.setState({suggestions: json.data}));
    }

    render() {
        const {suggestions, value} = this.state,
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
                    this.setState({selected: suggestion.id});
                    onChange(suggestion);
                }}
                getSuggestionValue={suggestion => suggestion.value}
                renderSuggestion={suggestion => <span>{suggestion.value}</span>}
                inputProps={{
                    placeholder,
                    value,
                    onChange: (event, {newValue}) => {
                        this.setState({value: newValue, selected: null});
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

export default Autocomplete;
