import React, { Component } from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import h from 'textCleanup/utils/helpers';

import './Content.css';

class Content extends Component {
    componentWillMount() {
        let { content_types } = this.props;
        this.setState({ content_types });
    }

    render() {
        let { data } = this.props,
            content = _.map(this.state.content_types, type => {
                return data[type] ? (
                    <p key={type}>
                        <b>
                            <u>{h.caseToWords(type)}</u>
                        </b>: {data[type]}
                    </p>
                ) : null;
            });
        return <div className="extraContent">{content}</div>;
    }
}

Content.propTypes = {
    data: PropTypes.shape({
        results_notes: PropTypes.string,
        system: PropTypes.string,
        organ: PropTypes.string,
        effect: PropTypes.string,
        effect_subtype: PropTypes.string,
    }).isRequired,
};

export default Content;
