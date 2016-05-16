import React, { Component, PropTypes } from 'react';

import ScoreCell from 'robAllTable/components/ScoreCell';
import './DomainCell.css';


class DomainCell extends Component {

    componentDidMount(){
        $('.tooltips').tooltip();
    }

    handleClick(){
        let { handleClick, domain } = this.props;
        handleClick({domain: domain.key});
    }

    render(){
        let { domain, handleClick } = this.props;
        return (
            <div className='domain-cell' style={{flex: domain.values.length}}>
                <div className='header-box' onClick={this.handleClick.bind(this)}>
                    <span className='domain-header'>{domain.key}</span>
                </div>
                <div className='score-row'>
                    {_.map(domain.values, (score) => {
                        return (
                            <ScoreCell key={score.id}
                                       score={score}
                                       handleClick={handleClick} />
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
    handleClick: PropTypes.func.isRequired,
};

export default DomainCell;
