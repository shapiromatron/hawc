import React, { Component, PropTypes } from 'react';
import moment from 'moment';


class StudyLabel extends Component {
    render() {
        return (
            <div className='study-label flex-1'>
                <a href={this.props.study.url}>{this.props.study.short_citation}</a><br/>
                <b>Date created: </b><span>{moment(this.props.study.created).format('L')}</span>
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
