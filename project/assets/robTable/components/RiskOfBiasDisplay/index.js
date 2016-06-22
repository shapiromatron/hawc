import React, { PropTypes } from 'react';
import ReactDOM from 'react-dom';

import DomainDisplay from 'robTable/components/DomainDisplay';


const RiskOfBiasDisplay = (props) => {
    return (
        <div className='riskofbias-display'>
            {_.map(props.active, (domain) => {
                return <DomainDisplay key={domain.key}
                                   domain={domain}
                                   config={props.config} />;
            })}
        </div>
    );
};

RiskOfBiasDisplay.propTypes = {
    active: PropTypes.arrayOf(PropTypes.object).isRequired,
    config: PropTypes.object,
};

export function renderRiskOfBiasDisplay(data, element){
    ReactDOM.render(<RiskOfBiasDisplay active={data.scores} config={data.config} />, element);
}

export default RiskOfBiasDisplay;
