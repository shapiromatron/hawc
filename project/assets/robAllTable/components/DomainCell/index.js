import React, { Component, PropTypes } from 'react';

import ScoreCell from 'robAllTable/components/ScoreCell';
import './DomainCell.css';


class DomainCell extends Component {

    render(){
        let { domain } = this.props;
        return (
            <div className='domain-cell' style={{flex: domain.values.length}}>
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
