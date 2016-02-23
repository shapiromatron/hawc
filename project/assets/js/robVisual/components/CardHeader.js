import React, { PropTypes, Component } from 'react';

import './CardHeader.css';

class CardHeader extends Component {

    getScoreQuality(score) {
        if (score >= 24){
            return 'high';
        } else if (score >= 18) {
            return 'medium';
        } else {
            return 'low';
        }
    }
    render() {
        let { endpoint, showModal, study } = this.props,
            score = study.qualities__score__sum,
            quality = this.getScoreQuality(score);
        return (
            <div className='cardHeader'>
                <h4 className='cardTitle'>
                    <span id={endpoint.id} onClick={showModal}>
                        {endpoint.name}
                    </span>
                    <span id={endpoint.id} onClick={showModal} className='cardCitation pull-right'>
                        {`[${endpoint.animal_group.experiment.study.short_citation}]`}
                    </span>
                </h4>
                <span className={`score ${quality}`}><b>
                    {score || '0'}
                </b></span>
            </div>
        );
    }
}

CardHeader.propTypes = {
    showModal: PropTypes.func.isRequired,
    endpoint: PropTypes.object.isRequired,
    study: PropTypes.object.isRequired,
};

export default CardHeader;
