import React, { Component, PropTypes } from 'react';
import fetch from 'isomorphic-fetch';
import AutoSuggest from 'react-autosuggest';

import h from 'mgmt/utils/helpers';
import './AutoSuggest.css';


class UserAutocomplete extends Component {

    constructor(props) {
        super(props);
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
            theme: {
                container:            'react-autosuggest__container',
                containerOpen:        'react-autosuggest__container--open',
                input:                'react-autosuggest__input',
                suggestionsContainer: 'react-autosuggest__suggestions-container',
                suggestionsList:      'react-autosuggest__suggestions-list',
                suggestion:           'react-autosuggest__suggestion',
                suggestionFocused:    'react-autosuggest__suggestion--focused',
                sectionContainer:     'react-autosuggest__section-container',
                sectionTitle:         'react-autosuggest__section-title',
            },
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
        const { theme, value, selected } = this.state;
        let input = 'react-autosuggest__input';
        switch (event) {
            case 'onBlur':
                // if !selected.id set ui-state-error
                break;
            case 'onChange':

                break;
            default:

        }
        return {
            ...theme,
            input,
        }
    }

    getSuggestionValue(suggestion) {
        return suggestion.value;
    }

    onChange(event, { newValue }) {
        this.setState({ value: newValue });
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
        this.setState({ selected: suggestion.id });
    }

    renderSuggestion(suggestion) {
        return <span>{suggestion.value}</span>;
    }

    render() {
        const { suggestions, value } = this.state,
            theme = this.getTheme(),
            inputProps = {
                placeholder: 'owner',
                value,
                onChange: this.onChange,
                omBlur: this.onBlur,
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
                focusFirstSuggestion={true}
                theme={theme}/>
        );
    }
}

UserAutocomplete.propTypes = {
};

export default UserAutocomplete;
