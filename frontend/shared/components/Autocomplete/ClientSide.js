import PropTypes from "prop-types";
import React, {Component} from "react";
import Autosuggest from "react-autosuggest";
import {createRoot} from "react-dom/client";
import h from "shared/utils/helpers";

import {theme} from "./constants";

class ClientSideAutosuggest extends Component {
    /*
    Client-side autocomplete; all possibilities are passed to the component via an input prop;
    the component just filters possibilities based on typing.
    */
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
                    const qry = h.escapeRegexString(value.trim()),
                        regex = new RegExp(qry, "i"),
                        suggestions =
                            qry.length == 0
                                ? options
                                : options.filter(v => regex.test(v)).slice(0, 30);
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
ClientSideAutosuggest.propTypes = {
    name: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired,
    options: PropTypes.arrayOf(PropTypes.string).isRequired,
};

const renderClientSideAutosuggest = function (el, name, value, options) {
    createRoot(el).render(<ClientSideAutosuggest name={name} value={value} options={options} />);
};

export {ClientSideAutosuggest, renderClientSideAutosuggest};
