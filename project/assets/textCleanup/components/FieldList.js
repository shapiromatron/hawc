import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

import h from 'textCleanup/utils/helpers';

class FieldList extends Component {
    renderField(field) {
        return (
            <li key={field}>
                <Link to={`${location.pathname}${field}/`}>{h.caseToWords(field)}</Link>
            </li>
        );
    }

    render() {
        const fields = this.props.fields;
        return (
            <div className="field_list">
                <ul>{fields.map(this.renderField)}</ul>
            </div>
        );
    }
}

FieldList.propTypes = {
    fields: PropTypes.arrayOf(PropTypes.string.isRequired).isRequired,
    location: PropTypes.string.isRequired,
};

export default FieldList;
