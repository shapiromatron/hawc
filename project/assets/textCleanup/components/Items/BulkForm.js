import React, { Component, PropTypes } from 'react';

import FormFieldError from 'textCleanup/components/FormFieldError';
import h from 'textCleanup/utils/helpers';

import DetailList from './DetailList';
import './BulkForm.css';


class BulkForm extends Component {

    constructor(props) {
        super(props);
        this.state = props.object;
        this.handleChange = this.handleChange.bind(this);
        this.handleCheckAll = this.handleCheckAll.bind(this);
        this.handleCheck = this.handleCheck.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.onDetailChange = this.onDetailChange.bind(this);
        this.showModal = this.showModal.bind(this);
        this._toggleDetails = this._toggleDetails.bind(this);
    }

    _toggleDetails() {
        this.setState({ showDetails: this.state.showDetails ? false : true });
    }

    handleSubmit(e) {
        e.preventDefault();
        let stale = this.props.items[0][this.state.field],
            { ids, detailIDs, showDetails } = this.state;
        // if detail edit and all checkboxes are not checked
        if (showDetails && detailIDs && detailIDs.length !== ids.length){
            this.props.handleDetailSubmit(Object.assign(
                {},
                _.omit(this.state, ['detailIDs', 'showDetails']),
                { ids: detailIDs, stale }));
        } else {
            this.props.handleBulkSubmit(Object.assign(
                {},
                _.omit(this.state, 'detailIDs'),
                { stale }));
        }
        this.setState({ detailIDs: []});
    }

    handleChange(e) {
        let obj = {};
        obj[this.props.params.field] = h.getValue(e.target);
        this.setState(obj);
    }

    handleCheckAll(e) {
        if (e.target.checked) {
            this.setState({ detailIDs: this.props.object.ids});
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

    // Uses eval() as the object supplying displayAsModal is dynamic.
    showModal(e){
        eval(this.props.modalClass + '.displayAsModal(e.target.id)');
    }

    render() {
        let { object, errors, field, params, items } = this.props,
            detailShow = this.state.showDetails ?
                'fa-minus-square' :
                'fa-plus-square',
            editButtonText = this.state.showDetails ?
                'Submit selected items' :
                'Submit bulk edit';
        return (
            <div className="stripe row">
                <form onSubmit={this.handleSubmit}>
                    <span className='bulk-element field span4'>
                        <button type='button'
                            title='Show/hide all items'
                            className='btn btn-inverse btn-mini'
                            onClick={this._toggleDetails}>
                            <i className={`fa ${detailShow}`}></i>
                        </button>
                        &nbsp;{field || `N/A`} ({items.length})
                    </span>
                    <span className={`${h.getInputDivClass(field, errors)} bulk-element span5`}>
                        <input name={field} className='form-control' type="text"
                            defaultValue={object[params.field]}
                            onChange={this.handleChange}/>
                        <FormFieldError errors={errors.name} />
                    </span>
                    <span className='bulk-element button span'>
                        <button type='submit' className='btn btn-primary'>{editButtonText}</button></span>
                </form>
                {this.state.showDetails ?
                    <DetailList
                        checkedRows={this.state.detailIDs}
                        items={items}
                        onDetailChange={this.onDetailChange}
                        showModal={this.showModal}
                    /> : null}
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

export default BulkForm;
