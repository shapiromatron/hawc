import React, {Component} from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";
import Autosuggest from "react-autosuggest";
import {theme} from "./constants";

// https://developer.mozilla.org/en/docs/Web/JavaScript/Guide/Regular_Expressions#Using_Special_Characters
const escapeRegexCharacters = function(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
};

class InlineAutosuggest extends Component {
    // Inline autosuggest; all possibilities are already client-side
    constructor(props) {
        super(props);
        this.state = {
            value: props.value,
            suggestions: [],
        };
    }
    render() {
        const {name, options} = this.props;
        const {value, suggestions} = this.state;
        return (
            <Autosuggest
                suggestions={suggestions}
                onSuggestionsFetchRequested={({value}) => {
                    const qry = escapeRegexCharacters(value.trim()),
                        regex = new RegExp(qry, "i"),
                        suggestions =
                            qry.length == 0 ? options : options.filter(v => regex.test(v));
                    this.setState({suggestions});
                }}
                onSuggestionsClearRequested={() => {
                    this.setState({suggestions: []});
                }}
                getSuggestionValue={d => d}
                renderSuggestion={d => <span>{d}</span>}
                inputProps={{
                    className: "form-control",
                    name,
                    value,
                    onChange: (event, {newValue}) => {
                        this.setState({value: newValue});
                    },
                }}
                theme={theme}
            />
        );
    }
}
InlineAutosuggest.propTypes = {
    name: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
    options: PropTypes.arrayOf(PropTypes.string).isRequired,
};

const renderInlineAutosuggest = function(el, name, value, options) {
    ReactDOM.render(<InlineAutosuggest name={name} value={value} options={options} />, el);
};

export {InlineAutosuggest, renderInlineAutosuggest};
