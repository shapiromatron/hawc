import React, { Component, PropTypes } from 'react';

import DetailList from 'components/Endpoint/DetailList';
import h from 'utils/helpers';
import FormFieldError from 'components/FormFieldError';
import Endpoint from 'Endpoint';
import Outcome from 'Outcome';


export default class BulkForm extends Component {

    constructor(props) {
        super(props);
        this.state = props.object;
    }

    _toggleDetails() {
        this.setState({ showDetails: this.state.showDetails ? false : true });
    }

    handleSubmit(e) {
        e.preventDefault();
        if (this.state.showDetails){
            this.props.handleDetailSubmit(Object.assign({}, _.omit(this.state, ['detailIDs', 'showDetails']), {ids: this.state.detailIDs}));
        } else {
            this.props.handleBulkSubmit(this.state);
        }
    }

    handleChange(e) {
        let obj = {};
        obj[this.props.params.field] = h.getValue(e.target);
        this.setState(obj);
    }

    handleCheckAll(e) {
        if (e.target.checked) {
            this.setState({ detailIDs: this.state.ids});
        } else {
            this.setState({ detailIDs: []});
        }
    }

    handleCheck(target){
        let detailIDs = this.state.detailIDs,
            id = parseInt(target.id);
        if (target.checked){
            this.setState({ detailIDs: detailIDs ? detailIDs.concat(id) : [id]});
        } else {
            this.setState({ detailIDs: _.without(detailIDs, id)});
        }
    }

    onDetailChange(e){
        (e.target.id === 'all') ? this.handleCheckAll(e) : this.handleCheck(e.target);
    }

    showModal(e){
        eval(this.props.modelEndpoint + '.displayAsModal(e.target.id)');
    }

    render() {
        let { object, errors, field, params, items } = this.props,
            detailShow = this.state.showDetails ? 'fa-minus-square' : 'fa-plus-square',
            editButtonText = this.state.showDetails ? 'Submit Selected Endpoints' : 'Submit Bulk Edit';
        return (
            <div className="stripe row">
                <form onSubmit={this.handleSubmit.bind(this)}>
                <span className='bulk-element field span4' onClick={this._toggleDetails.bind(this)}>
                    <i className={`fa ${detailShow}`}></i>
                    {field || `N/A`}
                </span>
                <span className={`${h.getInputDivClass(field, errors)} bulk-element span5`}>
                    <input name={field} className='form-control' type="text"
                        defaultValue={object[params.field]}
                        onChange={this.handleChange.bind(this)}/>
                    <FormFieldError errors={errors.name} />

                </span>
                <span className='bulk-element button span'><button type='submit' className='btn btn-primary'>{editButtonText}</button></span>
                </form>
                <div>{this.state.showDetails ?
                        <DetailList
                            checkedRows={this.state.detailIDs}
                            items={items}
                            field={field}
                            onDetailChange={this.onDetailChange.bind(this)}
                            showModal={this.showModal.bind(this)}
                        /> : null}
                </div>
            </div>
        );
    }
}

BulkForm.propTypes = {
    object: PropTypes.object.isRequired,
    errors: PropTypes.object.isRequired,
    field: PropTypes.string.isRequired,
    handleBulkSubmit: PropTypes.func.isRequired,
    handleDetailSubmit: PropTypes.func.isRequired,
    params: PropTypes.object.isRequired,
    items: PropTypes.array.isRequired,
};
