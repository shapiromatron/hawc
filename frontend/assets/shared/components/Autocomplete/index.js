import React, {Component} from "react";
import PropTypes from "prop-types";
import fetch from "isomorphic-fetch";
import AutoSuggest from "react-autosuggest";

import h from "shared/utils/helpers";
import "./Autocomplete.css";

class Autocomplete extends Component {
    constructor(props) {
        super(props);
        let {loaded} = props;
        this.defaultTheme = {
            container: "autocomplete__container",
            containerOpen: "autocomplete__container--open",
            input: "autocomplete__input",
            suggestionsContainer: "autocomplete__suggestions-container",
            suggestionsList: "autocomplete__suggestions-list",
            suggestion: "autocomplete__suggestion",
            suggestionFocused: "autocomplete__suggestion--focused",
            sectionContainer: "autocomplete__section-container",
            sectionTitle: "autocomplete__section-title",
        };
        this.getSuggestionValue = this.getSuggestionValue.bind(this);
        this.getTheme = this.getTheme.bind(this);
        this.onBlur = this.onBlur.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onSuggestionsClearRequested = this.onSuggestionsClearRequested.bind(this);
        this.onSuggestionsFetchRequested = this.onSuggestionsFetchRequested.bind(this);
        this.onSuggestionSelected = this.onSuggestionSelected.bind(this);
        this.selectionIsInvalid = this.selectionIsInvalid.bind(this);

        this.state = {
            value: loaded.display ? loaded.display : "",
            suggestions: [],
            selected: loaded.id ? loaded.id : null,
            theme: {...this.defaultTheme},
        };
    }

    getTheme(event) {
        const {theme} = this.state;
        let input = this.defaultTheme.input;
        if (this.selectionIsInvalid(event)) {
            input = `${input} autocomplete-error`;
        }
        return {
            ...theme,
            input,
        };
    }

    selectionIsInvalid(event) {
        const {selected} = this.state;
        return event.type === "blur" && !selected;
    }

    getSuggestionValue(suggestion) {
        return suggestion.value;
    }

    onBlur(event, {focusedSuggestion}) {
        this.setState({
            theme: this.getTheme(event),
        });
    }

    onChange(event, {newValue}) {
        this.setState({
            value: newValue,
            theme: this.getTheme(event),
            selected: null,
        });
    }

    onSuggestionsFetchRequested({value}) {
        fetch(`${this.props.url}&term=${value}`, h.fetchGet)
            .then(response => response.json())
            .then(json => {
                this.setState({suggestions: json.data});
            });
    }

    onSuggestionsClearRequested() {
        this.setState({
            suggestions: [],
        });
    }

    onSuggestionSelected(event, {suggestion}) {
        this.setState({
            selected: suggestion.id,
        });
        this.props.onChange(suggestion);
    }

    renderSuggestion(suggestion) {
        return <span>{suggestion.value}</span>;
    }

    render() {
        const {suggestions, theme, value} = this.state,
            {placeholder, id} = this.props,
            inputProps = {
                placeholder,
                value,
                onChange: this.onChange,
                onBlur: this.onBlur,
            };
        return (
            <AutoSuggest
                id={id}
                suggestions={suggestions}
                onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
                onSuggestionsClearRequested={this.onSuggestionsClearRequested}
                onSuggestionSelected={this.onSuggestionSelected}
                getSuggestionValue={this.getSuggestionValue}
                renderSuggestion={this.renderSuggestion}
                inputProps={inputProps}
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
};

export default Autocomplete;
