import React, { Component, PropTypes } from 'react';
import fetch from 'isomorphic-fetch';
import AutoSuggest from 'react-autosuggest';

import h from 'shared/utils/helpers';
import './Autocomplete.css';


class Autocomplete extends Component {

    constructor(props) {
        super(props);
        this.defaultTheme = {
            container:            'autocomplete__container',
            containerOpen:        'autocomplete__container--open',
            input:                'autocomplete__input',
            suggestionsContainer: 'autocomplete__suggestions-container',
            suggestionsList:      'autocomplete__suggestions-list',
            suggestion:           'autocomplete__suggestion',
            suggestionFocused:    'autocomplete__suggestion--focused',
            sectionContainer:     'autocomplete__section-container',
            sectionTitle:         'autocomplete__section-title',
        };
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
        let { url, assessment } = this.props;
        this.url = `${url}?related=${assessment}`;
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

    onSuggestionsFetchRequested({ value }) {
        fetch(`${this.url}&term=${value}`, h.fetchGet)
            .then((response) => response.json())
            .then((json) => { this.setState({suggestions: json.data}); });
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
                placeholder: this.props.placeholder,
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

Autocomplete.propTypes = {
    assessment: PropTypes.number.isRequired,
    placeholder: PropTypes.string.isRequired,
    url: PropTypes.string.isRequired,
};

export default Autocomplete;
