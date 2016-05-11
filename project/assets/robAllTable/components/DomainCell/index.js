import React, { Component, PropTypes } from 'react';

import ScoreCell from 'robAllTable/components/ScoreCell';
import './DomainCell.css';


class DomainCell extends Component {

    render(){
        let { domain, domain_n } = this.props,
            cellLength = domain.values.length / domain_n;
        return (
            <div className='domain-cell' style={{flex: cellLength}}>
                <div className='header-box'>
                    <span className='domain-header'>{domain.key}</span>
                </div>
                <div className='score-row'>
                    {_.map(domain.values, (score) => {
                        return (
                            <ScoreCell key={score.id} score={score} />
                        );
                    })}
                </div>
            </div>

        );
    }
}

DomainCell.propTypes = {
    domain: PropTypes.shape({
        key: PropTypes.string.isRequired,
        values: PropTypes.array.isRequired,
    }).isRequired,
};

export default DomainCell;
