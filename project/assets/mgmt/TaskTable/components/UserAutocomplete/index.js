import React, { Component, PropTypes } from 'react';
import fetch from 'isomorphic-fetch';
import AutoSuggest from 'react-autosuggest';

import h from 'mgmt/utils/helpers';
import './AutoSuggest.css';


class UserAutocomplete extends Component {

    constructor(props) {
        super(props);
        this.defaultTheme = {
            container:            'react-autosuggest__container',
            containerOpen:        'react-autosuggest__container--open',
            input:                'react-autosuggest__input',
            suggestionsContainer: 'react-autosuggest__suggestions-container',
            suggestionsList:      'react-autosuggest__suggestions-list',
            suggestion:           'react-autosuggest__suggestion',
            suggestionFocused:    'react-autosuggest__suggestion--focused',
            sectionContainer:     'react-autosuggest__section-container',
            sectionTitle:         'react-autosuggest__section-title',
        };
        this.fetchUserMatch = this.fetchUserMatch.bind(this);
        this.getSuggestionValue = this.getSuggestionValue.bind(this);
        this.getTheme = this.getTheme.bind(this);
        this.onBlur = this.onBlur.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onSuggestionsClearRequested = this.onSuggestionsClearRequested.bind(this);
        this.onSuggestionsFetchRequested = this.onSuggestionsFetchRequested.bind(this);
        this.onSuggestionSelected = this.onSuggestionSelected.bind(this);

        this.state = {
            value: '',
            suggestions: [],
            selected: null,
            theme: { ...this.defaultTheme },
        };

    }

    componentWillMount() {
        this.url = `/selectable/myuser-assessmentteammemberorhigherlookup/?related=${this.props.task.study.assessment}`;
    }

    fetchUserMatch({ value }) {
        fetch(`${this.url}&term=${value}`, h.fetchGet)
            .then((response) => response.json())
            .then((json) => { this.setState({suggestions: json.data}); });
    }

    getTheme(event) {
        const { theme, selected } = this.state;
        let input = this.defaultTheme.input;
        if (event.type === 'blur' && !selected) {
            input = `${input} autocomplete-error`;
        }
        return {
            ...theme,
            input,
        };
    }

    getSuggestionValue(suggestion) {
        return suggestion.value;
    }

    onBlur(event, { focusedSuggestion }) {
        this.setState({
            theme: this.getTheme(event),
        });
    }

    onChange(event, { newValue }) {
        this.setState({
            value: newValue,
            theme: this.getTheme(event),
            selected: null,
        });
    }

    onSuggestionsFetchRequested(value) {
        this.fetchUserMatch(value);
    }

    onSuggestionsClearRequested() {
        this.setState({
            suggestions: [],
        });
    }

    onSuggestionSelected(event, { suggestion }) {
        this.setState({
            selected: suggestion.id,
        });
    }

    renderSuggestion(suggestion) {
        return <span>{suggestion.value}</span>;
    }

    render() {
        const { suggestions, theme, value } = this.state,
            inputProps = {
                placeholder: 'owner',
                value,
                onChange: this.onChange,
                onBlur: this.onBlur,
            };
        return (
            <AutoSuggest className='ui-state-error'
                suggestions={suggestions}
                onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
                onSuggestionsClearRequested={this.onSuggestionsClearRequested}
                onSuggestionSelected={this.onSuggestionSelected}
                getSuggestionValue={this.getSuggestionValue}
                renderSuggestion={this.renderSuggestion}
                inputProps={inputProps}
                theme={theme}/>
        );
    }
}

UserAutocomplete.propTypes = {
};

export default UserAutocomplete;
