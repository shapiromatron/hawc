import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";

import ScoreDisplay from "riskofbias/robTable/components/ScoreDisplay";

const CrossStudyDisplay = props => {
    let {domain, metric, scores, config} = props;
    scores = scores[0].values[0].values;
    return (
        <div className="cross-study-display">
            <h3>{domain}</h3>
            <h4>{metric.name}</h4>
            {metric.hide_description ? null : (
                <div dangerouslySetInnerHTML={{__html: metric.description}} />
            )}
            {_.map(scores, (rob, i) => {
                return (
                    <div key={rob.id}>
                        <h4>
                            <a target="_blank" rel="noopener noreferrer" href={rob.study.url}>
                                {rob.study.name}
                            </a>
                        </h4>
                        <ScoreDisplay key={i} score={rob} config={config} />
                    </div>
                );
            })}
        </div>
    );
};

CrossStudyDisplay.propTypes = {
    domain: PropTypes.string.isRequired,
    metric: PropTypes.shape({
        name: PropTypes.string.isRequired,
        description: PropTypes.string.isRequired,
        hide_description: PropTypes.bool.isRequired,
    }).isRequired,
    scores: PropTypes.arrayOf(
        PropTypes.shape({
            values: PropTypes.arrayOf(
                PropTypes.shape({
                    values: PropTypes.arrayOf(
                        PropTypes.shape({
                            id: PropTypes.number.isRequired,
                            study: PropTypes.shape({
                                url: PropTypes.string.isRequired,
                                name: PropTypes.string.isRequired,
                            }).isRequired,
                            author: PropTypes.object.isRequired,
                            notes: PropTypes.string,
                            score_description: PropTypes.string.isRequired,
                            score_symbol: PropTypes.string.isRequired,
                            score_shade: PropTypes.string.isRequired,
                        })
                    ).isRequired,
                })
            ).isRequired,
        })
    ).isRequired,
};

export function renderCrossStudyDisplay(data, element) {
    // eslint-disable-next-line react/no-render-return-value
    return ReactDOM.render(<CrossStudyDisplay {...data} />, element);
}

export default CrossStudyDisplay;
