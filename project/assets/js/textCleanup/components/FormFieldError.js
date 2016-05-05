import _ from 'underscore';
import React from 'react';


class FormFieldError extends React.Component {

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

export default FormFieldError;
