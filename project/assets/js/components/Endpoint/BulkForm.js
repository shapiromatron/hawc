import React, { Component, PropTypes } from 'react';

import h from 'utils/helpers';
import FormFieldError from 'components/FormFieldError';


export default class BulkForm extends Component {

    handleSubmit(){

    }
    handleChange(){

    }

    render() {
        let { object, errors, field, params } = this.props;
        console.log(params)
        return (
            <div  className="stripe row" onSubmit={this.handleSubmit.bind(this)}>
                <span className='bulk-element field span4'>{field || `N/A`}</span>
                <span className={`${h.getInputDivClass(field, errors)} bulk-element span5`}>
                    <input name={field} className='form-control' type="text"
                        value={object[field][params.field]}
                        onChange={this.handleChange.bind(this)}/>
                    <FormFieldError errors={errors.name} />

                </span>
                <span className='bulk-element span2'><button className='btn btn-primary'>Submit Bulk Edit</button></span>
            </div>
        );
    }
}

BulkForm.propTypes = {
    object: PropTypes.object.isRequired,
    errors: PropTypes.object.isRequired,
    field: PropTypes.string.isRequired,
    handleSubmit: PropTypes.func.isRequired,
};
