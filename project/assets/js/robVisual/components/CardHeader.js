import React, { PropTypes, Component } from 'react';
import _ from 'underscore';

import './CardHeader.css';


class CardHeader extends Component {

    getScoreQuality(score) {
        if (_.isNull(score))
            return 'not-applicable';

        if (score >= 24){
            return 'high';
        } else if (score >= 18) {
            return 'medium';
        } else {
            return 'low';
        }
    }
    render() {
        let { endpoint, showEndpointModal, showStudyModal, study, citation } = this.props,
            score = study.qualities__score__sum,
            quality = this.getScoreQuality(score);
        return (
            <div className='cardHeader'>
                <h4 className='cardTitle'>
                    <span className={`pull-right score ${quality}`}><b>
                        {score || 'N/A'}
                    </b></span>
                    <span
                        className='modalAnchor'
                        id={endpoint.id}
                        onClick={showEndpointModal}>
                        {endpoint.name}
                    </span>
                    <br />
                    <span id={endpoint.animal_group.experiment.study.id}
                          onClick={showStudyModal}
                          className='modalAnchor cardCitation'>
                        {`(${citation})`}
                    </span>
                </h4>

            </div>
        );
    }
}

CardHeader.propTypes = {
    showEndpointModal: PropTypes.func.isRequired,
    showStudyModal: PropTypes.func.isRequired,
    endpoint: PropTypes.object.isRequired,
    study: PropTypes.object.isRequired,
};

export default CardHeader;
