import React, { Component, PropTypes } from 'react';

import DetailList from 'components/Endpoint/DetailList';
import h from 'utils/helpers';
import FormFieldError from 'components/FormFieldError';


export default class BulkForm extends Component {

    constructor(props) {
        super(props);
        this.state = props.object;
    }

    handleSubmit(e){
        e.preventDefault();
        this.props.handleSubmit(this.state);
    }

    handleChange(e){
        let obj = {};
        obj[this.props.params.field] = h.getValue(e.target);
        this.setState(obj);
    }

    _toggleDetails() {
        this.setState({ showDetails: this.state.showDetails ? false : true });
    }

    checkDetails(e){
    }


    render() {
        let { object, errors, field, params, items } = this.props;
        return (
            <div className="stripe row">
                <form onSubmit={this.handleSubmit.bind(this)}>
                <span className='bulk-element field span4'>
                    <i className='fa fa-plus-square' onClick={this._toggleDetails.bind(this)}></i>
                    {field || `N/A`}</span>
                <span className={`${h.getInputDivClass(field, errors)} bulk-element span5`}>
                    <input name={field} className='form-control' type="text"
                        defaultValue={object[params.field]}
                        onChange={this.handleChange.bind(this)}/>
                    <FormFieldError errors={errors.name} />

                </span>
                <span className='bulk-element span2'><button type='submit' className='btn btn-primary'>Submit Bulk Edit</button></span>
                </form>
                <div>{this.state.showDetails ? <DetailList items={items} field={field} checkDetails={this.checkDetails.bind(this)}/> : null}</div>
            </div>
        );
    }
}

BulkForm.propTypes = {
    object: PropTypes.object.isRequired,
    errors: PropTypes.object.isRequired,
    field: PropTypes.string.isRequired,
    handleSubmit: PropTypes.func.isRequired,
    params: PropTypes.object.isRequired,
    items: PropTypes.array.isRequired,
};
