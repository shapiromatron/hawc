import React from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';

import DomainDisplay from 'riskofbias/robTable/components/DomainDisplay';

const RiskOfBiasDisplay = (props) => {
    return (
        <div className="riskofbias-display">
            {props.config.show_study ? renderStudyHeader(props) : null}
            {_.map(props.active, (domain) => {
                return <DomainDisplay key={domain.key} domain={domain} config={props.config} />;
            })}
        </div>
    );
};

const renderStudyHeader = (props) => {
    return (
        <h3>
            <a href={props.config.study.url}>{props.config.study.name}</a>
        </h3>
    );
};

RiskOfBiasDisplay.propTypes = {
    active: PropTypes.arrayOf(PropTypes.object).isRequired,
    config: PropTypes.object,
};

export function renderRiskOfBiasDisplay(data, element) {
    ReactDOM.render(<RiskOfBiasDisplay active={data.scores} config={data.config} />, element);
}

export default RiskOfBiasDisplay;
