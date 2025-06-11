import _ from "lodash";
import PropTypes from "prop-types";
import React from "react";
import ReactDOM from "react-dom";
import DomainDisplay from "riskofbias/robTable/components/DomainDisplay";

const RiskOfBiasDisplay = props => {
    return (
        <div className="riskofbias-display">
            {props.config.showStudyHeader ? (
                <h3>
                    <a href={props.config.studyUrl}>{props.config.studyName}</a>
                </h3>
            ) : null}
            {_.map(props.active, domain => {
                return <DomainDisplay key={domain.key} domain={domain} config={props.config} />;
            })}
        </div>
    );
};

RiskOfBiasDisplay.propTypes = {
    active: PropTypes.arrayOf(PropTypes.object).isRequired,
    config: PropTypes.shape({
        showStudyHeader: PropTypes.bool,
        studyUrl: PropTypes.string,
        studyName: PropTypes.string,
    }),
};

export function renderRiskOfBiasDisplay(data, element) {
    ReactDOM.render(<RiskOfBiasDisplay active={data.scores} config={data.config} />, element);
}

export default RiskOfBiasDisplay;
