import React, { Component, PropTypes } from 'react';
import moment from 'moment';


class StudyLabel extends Component {
    render() {
        return (
            <div className='study-label flex-1'>
                <label className='control-label' htmlFor={`short-citation-${this.props.study.id}`}>Short citation</label>
                <a id={`short-citation-${this.props.study.id}`} href={this.props.study.url}>
                    {this.props.study.short_citation}
                </a>
                <br/>
                <label className='control-label' htmlFor={`creation-date-${this.props.study.id}`}>Created on</label>
                <span id={`creation-date-${this.props.study.id}`}>{moment(this.props.study.created).format('MMM Do YYYY')}</span>
            </div>
        );
    }
}

StudyLabel.propTypes = {
    study: PropTypes.shape({
        short_citation: PropTypes.string.isRequired,
        created: PropTypes.string.isRequired,
        id: PropTypes.number.isRequired,
        url: PropTypes.string.isRequired,
    }).isRequired,
};

export default StudyLabel;
