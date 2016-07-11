import React, { Component, PropTypes } from 'react';

import ScoreCell from 'robTable/components/ScoreCell';
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
                            <ScoreCell key={score.values[0].id}
                                       score={score.values[0]}
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
        values: PropTypes.arrayOf(PropTypes.shape({
            values: PropTypes.arrayOf(PropTypes.shape({
                id: PropTypes.number.isRequired,
                score_symbol: PropTypes.string.isRequired,
                score_shade: PropTypes.string.isRequired,
                domain_name: PropTypes.string.isRequired,
                metric: PropTypes.shape({
                    metric: PropTypes.string.isRequired,
                }).isRequired,
            })).isRequired,
        })).isRequired,
    }).isRequired,
    handleClick: PropTypes.func.isRequired,
};

export default DomainCell;
