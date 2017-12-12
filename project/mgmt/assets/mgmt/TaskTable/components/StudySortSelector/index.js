import React, { Component } from 'react';
import PropTypes from 'prop-types';

import h from 'mgmt/utils/helpers';

class StudySortSelector extends Component {
    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this);
        this.state = props.studySorting;
        this.defaults = {
            order: props.orderOptions[0],
            field: props.fieldOptions[0],
        };
    }

    onChange({ currentTarget }) {
        const { name, id } = currentTarget,
            { field, order } = this.state;
        this.props.handleChange({
            order: order ? order : this.defaults.order,
            field: field ? field : this.defaults.field,
            [name]: id,
        });
        this.setState({ [name]: id });
    }

    render() {
        const {
            className,
            fieldOptions,
            orderOptions,
            studySorting,
        } = this.props;
        return (
            <div className={className}>
                <div className="flexRow-container">
                    <div className="flex-1">
                        <label
                            className="control-label"
                            htmlFor="study_sorting-field"
                        >
                            Sort studies by:
                        </label>
                        <form id="study_sorting-field">
                            {fieldOptions.map((field) => {
                                return (
                                    <label key={field} htmlFor={field}>
                                        <input
                                            onChange={this.onChange}
                                            checked={
                                                studySorting.field == field
                                            }
                                            type="radio"
                                            id={field}
                                            name="field"
                                            style={{ margin: '0 4px' }}
                                        />
                                        {h.caseToWords(field)}
                                    </label>
                                );
                            })}
                        </form>
                    </div>

                    <div className="flex-1">
                        <label
                            className="control-label"
                            htmlFor="study_sorting-order"
                        >
                            Order studies by:
                        </label>
                        <form id="study_sorting-order">
                            {orderOptions.map((order) => {
                                return (
                                    <label key={order} htmlFor={order}>
                                        <input
                                            onChange={this.onChange}
                                            checked={
                                                studySorting.order === order
                                            }
                                            type="radio"
                                            id={order}
                                            name="order"
                                            style={{ margin: '0 4px' }}
                                        />
                                        {h.caseToWords(order)}
                                    </label>
                                );
                            })}
                        </form>
                    </div>
                </div>
            </div>
        );
    }
}

StudySortSelector.propTypes = {
    handleChange: PropTypes.func.isRequired,
    studySorting: PropTypes.shape({
        field: PropTypes.string,
        order: PropTypes.string,
    }).isRequired,
    fieldOptions: PropTypes.array.isRequired,
    orderOptions: PropTypes.array.isRequired,
};

export default StudySortSelector;
