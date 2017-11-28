import _ from 'underscore';
import React, { Component } from 'react';
import PropTypes from 'prop-types';


class FormFieldError extends Component {

    render() {
        if(_.isUndefined(this.props.errors)) return null;
        return (
            <div>
                {this.props.errors.map(function(d, i){
                    return <p key={i} className="help-block"><strong>{d}</strong></p>;
                })}
            </div>
        );
    }
}

FormFieldError.propTypes = {
    errors: PropTypes.arrayOf(
        PropTypes.string
    ),
};

export default FormFieldError;
