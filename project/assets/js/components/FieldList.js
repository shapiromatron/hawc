import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';
import urls from '../constants/urls';
import h from '../utils/helpers';

export default class FieldList extends Component {
    renderField(field) {
        return (
            <li key={field}>
                <Link to={urls.endpoints.url}>{h.caseToWords(field)}</Link>
            </li>
        );
    }

    render() {
        const fields = this.props.fields;

        return (
            <div className='field_list'>
                <h2 className='field_list_title'>{urls.fields.name}</h2>
                <ul>
                    {fields.map(this.renderField)}
                </ul>
            </div>
        );
    }
}

FieldList.propTypes = {
    fields: PropTypes.arrayOf(
        PropTypes.string.isRequired
    ).isRequired,
};
